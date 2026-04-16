from datetime import timedelta
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.utils import timezone

from apps.catalog.models import ItemCopy
from apps.notifications.services import notify_overdue_loan, notify_reservation_available
from apps.users.models import Patron, PatronBlock

from .models import Loan, Reservation


def get_fine_rate() -> Decimal:
    return Decimal(str(getattr(settings, 'LOAN_FINE_PER_DAY', '1.50')))


def get_overdue_block_reason() -> str:
    return getattr(settings, 'OVERDUE_BLOCK_REASON', 'Automatic block due to overdue loans')


def get_reservation_hold_hours() -> int:
    return int(getattr(settings, 'RESERVATION_HOLD_HOURS', 48))


def get_days_overdue(loan: Loan, now=None) -> int:
    reference = now or timezone.now()
    if loan.returned_at or loan.due_at >= reference:
        return 0
    return max((reference.date() - loan.due_at.date()).days, 1)


def calculate_fine_amount(days_overdue: int) -> Decimal:
    if days_overdue <= 0:
        return Decimal('0.00')
    amount = get_fine_rate() * Decimal(days_overdue)
    return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def rebalance_reservation_queue(bibliographic_record) -> None:
    active_reservations = Reservation.objects.filter(
        bibliographic_record=bibliographic_record,
        status__in=[Reservation.Status.QUEUED, Reservation.Status.AVAILABLE],
    ).order_by('queue_position', 'created_at')

    for index, reservation in enumerate(active_reservations, start=1):
        if reservation.queue_position != index:
            reservation.queue_position = index
            reservation.save(update_fields=['queue_position', 'updated_at'])


def set_reservation_available(reservation: Reservation, item_copy: ItemCopy, now=None):
    reference = now or timezone.now()
    reservation.status = Reservation.Status.AVAILABLE
    reservation.fulfilled_item_copy = item_copy
    reservation.expires_at = reference + timedelta(hours=get_reservation_hold_hours())
    reservation.save(update_fields=['status', 'fulfilled_item_copy', 'expires_at', 'updated_at'])

    if item_copy.status != ItemCopy.Status.RESERVED:
        item_copy.status = ItemCopy.Status.RESERVED
        item_copy.save(update_fields=['status', 'updated_at'])

    notify_reservation_available(reservation)
    return reservation


def make_next_reservation_available(item_copy: ItemCopy, now=None):
    next_reservation = Reservation.objects.filter(
        bibliographic_record=item_copy.bibliographic_record,
        status=Reservation.Status.QUEUED,
    ).order_by('queue_position', 'created_at').first()

    if not next_reservation:
        if item_copy.status != ItemCopy.Status.AVAILABLE:
            item_copy.status = ItemCopy.Status.AVAILABLE
            item_copy.save(update_fields=['status', 'updated_at'])
        return None

    return set_reservation_available(next_reservation, item_copy, now=now)


def fulfill_available_reservation_for_loan(loan: Loan):
    reservation = Reservation.objects.filter(
        patron=loan.patron,
        bibliographic_record=loan.item_copy.bibliographic_record,
        status=Reservation.Status.AVAILABLE,
    ).order_by('queue_position', 'created_at').first()

    if reservation is None:
        return None

    update_fields = ['status', 'updated_at']
    reservation.status = Reservation.Status.FULFILLED
    if reservation.fulfilled_item_copy_id != loan.item_copy_id:
        reservation.fulfilled_item_copy = loan.item_copy
        update_fields.append('fulfilled_item_copy')
    reservation.save(update_fields=update_fields)
    rebalance_reservation_queue(loan.item_copy.bibliographic_record)
    return reservation


def process_expired_reservations(now=None) -> dict:
    reference = now or timezone.now()
    summary = {
        'reservations_expired': 0,
        'reservations_promoted': 0,
        'copies_released': 0,
    }

    expired_reservations = list(
        Reservation.objects.select_related('fulfilled_item_copy', 'bibliographic_record').filter(
            status=Reservation.Status.AVAILABLE,
            expires_at__isnull=False,
            expires_at__lt=reference,
        )
    )

    for reservation in expired_reservations:
        reservation.status = Reservation.Status.EXPIRED
        reservation.save(update_fields=['status', 'updated_at'])
        summary['reservations_expired'] += 1

        item_copy = reservation.fulfilled_item_copy
        rebalance_reservation_queue(reservation.bibliographic_record)

        if item_copy is None:
            continue

        promoted_reservation = make_next_reservation_available(item_copy, now=reference)
        if promoted_reservation is not None:
            summary['reservations_promoted'] += 1
        else:
            summary['copies_released'] += 1

    return summary


def sync_patron_overdue_status(patron: Patron) -> str:
    reason = get_overdue_block_reason()
    auto_block = patron.blocks.filter(reason=reason).first()
    has_overdue_loans = patron.loans.filter(status=Loan.Status.OVERDUE, returned_at__isnull=True).exists()

    if has_overdue_loans:
        changed = False
        if auto_block is None:
            PatronBlock.objects.create(patron=patron, reason=reason, is_active=True)
            changed = True
        elif not auto_block.is_active:
            auto_block.is_active = True
            auto_block.save(update_fields=['is_active', 'updated_at'])
            changed = True

        if patron.status != Patron.Status.BLOCKED:
            patron.status = Patron.Status.BLOCKED
            patron.save(update_fields=['status', 'updated_at'])
            changed = True
        return 'blocked' if changed else 'unchanged'

    released = False
    if auto_block and auto_block.is_active:
        auto_block.is_active = False
        auto_block.save(update_fields=['is_active', 'updated_at'])
        released = True

    remaining_blocks = patron.blocks.filter(is_active=True)
    if auto_block:
        remaining_blocks = remaining_blocks.exclude(id=auto_block.id)

    if patron.status == Patron.Status.BLOCKED and not remaining_blocks.exists():
        patron.status = Patron.Status.ACTIVE
        patron.save(update_fields=['status', 'updated_at'])
        released = True

    return 'released' if released else 'unchanged'


def process_overdue_loans(now=None) -> dict:
    reference = now or timezone.now()
    summary = {
        'loans_marked_overdue': 0,
        'loans_reopened': 0,
        'patrons_blocked': 0,
        'patrons_released': 0,
        'overdue_notifications_sent': 0,
    }

    loans = Loan.objects.select_related('patron', 'item_copy__bibliographic_record').filter(
        status__in=[Loan.Status.OPEN, Loan.Status.OVERDUE],
        returned_at__isnull=True,
    )
    touched_patron_ids = set(
        PatronBlock.objects.filter(reason=get_overdue_block_reason(), is_active=True).values_list('patron_id', flat=True)
    )

    for loan in loans:
        touched_patron_ids.add(loan.patron_id)
        days_overdue = get_days_overdue(loan, reference)

        if days_overdue > 0:
            fine_amount = calculate_fine_amount(days_overdue)
            updated_fields = []
            newly_overdue = loan.status != Loan.Status.OVERDUE
            if newly_overdue:
                loan.status = Loan.Status.OVERDUE
                updated_fields.append('status')
                summary['loans_marked_overdue'] += 1
            if loan.fine_amount != fine_amount:
                loan.fine_amount = fine_amount
                updated_fields.append('fine_amount')
            if updated_fields:
                updated_fields.append('updated_at')
                loan.save(update_fields=updated_fields)
            if newly_overdue:
                notify_overdue_loan(loan, days_overdue=days_overdue)
                summary['overdue_notifications_sent'] += 1
        elif loan.status == Loan.Status.OVERDUE or loan.fine_amount != Decimal('0.00'):
            loan.status = Loan.Status.OPEN
            loan.fine_amount = Decimal('0.00')
            loan.save(update_fields=['status', 'fine_amount', 'updated_at'])
            summary['loans_reopened'] += 1

    for patron in Patron.objects.filter(id__in=touched_patron_ids):
        result = sync_patron_overdue_status(patron)
        if result == 'blocked':
            summary['patrons_blocked'] += 1
        elif result == 'released':
            summary['patrons_released'] += 1

    return summary
