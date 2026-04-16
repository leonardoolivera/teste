from .models import EmailNotificationLog
from .tasks import deliver_email_notification


def queue_email_notification(*, notification_type: str, recipient_email: str, subject: str, body: str, target_model: str, target_id: str, payload: dict | None = None):
    notification = EmailNotificationLog.objects.create(
        notification_type=notification_type,
        recipient_email=recipient_email,
        subject=subject,
        body=body,
        target_model=target_model,
        target_id=target_id,
        payload=payload or {},
    )
    deliver_email_notification.delay(str(notification.id))
    return notification


def notify_loan_created(loan):
    subject = f'Emprestimo registrado: {loan.item_copy.bibliographic_record.title}'
    body = (
        f'Ola, {loan.patron.full_name}.\n\n'
        f'Seu emprestimo foi registrado com sucesso.\n'
        f'Titulo: {loan.item_copy.bibliographic_record.title}\n'
        f'Patrimonio: {loan.item_copy.asset_code}\n'
        f'Vencimento: {loan.due_at:%d/%m/%Y %H:%M}\n'
    )
    return queue_email_notification(
        notification_type=EmailNotificationLog.NotificationType.LOAN_CREATED,
        recipient_email=loan.patron.email,
        subject=subject,
        body=body,
        target_model='Loan',
        target_id=str(loan.id),
        payload={'patron_id': str(loan.patron_id), 'item_copy_id': str(loan.item_copy_id)},
    )


def notify_return_receipt_created(receipt):
    loan = receipt.loan
    subject = f'Devolucao registrada: {loan.item_copy.bibliographic_record.title}'
    body = (
        f'Ola, {loan.patron.full_name}.\n\n'
        f'Sua devolucao foi registrada com sucesso.\n'
        f'Titulo: {loan.item_copy.bibliographic_record.title}\n'
        f'Patrimonio: {loan.item_copy.asset_code}\n'
        f'Token de devolucao: {receipt.return_token}\n'
    )
    return queue_email_notification(
        notification_type=EmailNotificationLog.NotificationType.RETURN_RECEIPT,
        recipient_email=loan.patron.email,
        subject=subject,
        body=body,
        target_model='ReturnReceipt',
        target_id=str(receipt.id),
        payload={'loan_id': str(loan.id), 'return_token': receipt.return_token},
    )


def notify_overdue_loan(loan, *, days_overdue: int):
    subject = f'Atraso identificado: {loan.item_copy.bibliographic_record.title}'
    body = (
        f'Ola, {loan.patron.full_name}.\n\n'
        f'Identificamos atraso na devolucao do item abaixo.\n'
        f'Titulo: {loan.item_copy.bibliographic_record.title}\n'
        f'Patrimonio: {loan.item_copy.asset_code}\n'
        f'Vencimento original: {loan.due_at:%d/%m/%Y %H:%M}\n'
        f'Dias em atraso: {days_overdue}\n'
        f'Multa atual: R$ {loan.fine_amount}\n\n'
        'Regularize o atendimento com a biblioteca para evitar novas restricoes.\n'
    )
    return queue_email_notification(
        notification_type=EmailNotificationLog.NotificationType.OVERDUE_REMINDER,
        recipient_email=loan.patron.email,
        subject=subject,
        body=body,
        target_model='Loan',
        target_id=str(loan.id),
        payload={
            'patron_id': str(loan.patron_id),
            'item_copy_id': str(loan.item_copy_id),
            'days_overdue': days_overdue,
            'fine_amount': str(loan.fine_amount),
        },
    )


def notify_reservation_available(reservation):
    fulfilled_item = reservation.fulfilled_item_copy
    pickup_branch = reservation.pickup_branch
    subject = f'Reserva disponivel para retirada: {reservation.bibliographic_record.title}'
    body = (
        f'Ola, {reservation.patron.full_name}.\n\n'
        f'Sua reserva esta disponivel para retirada.\n'
        f'Titulo: {reservation.bibliographic_record.title}\n'
        f'Biblioteca: {pickup_branch.campus.name} - {pickup_branch.name}\n'
        f'Patrimonio reservado: {fulfilled_item.asset_code if fulfilled_item else "a definir"}\n'
        f'Prazo de retirada: {reservation.expires_at:%d/%m/%Y %H:%M}\n\n'
        'Se o prazo expirar, a reserva seguira automaticamente para a proxima pessoa da fila.\n'
    )
    return queue_email_notification(
        notification_type=EmailNotificationLog.NotificationType.RESERVATION_AVAILABLE,
        recipient_email=reservation.patron.email,
        subject=subject,
        body=body,
        target_model='Reservation',
        target_id=str(reservation.id),
        payload={
            'patron_id': str(reservation.patron_id),
            'record_id': str(reservation.bibliographic_record_id),
            'item_copy_id': str(reservation.fulfilled_item_copy_id) if reservation.fulfilled_item_copy_id else '',
            'expires_at': reservation.expires_at.isoformat() if reservation.expires_at else '',
        },
    )


