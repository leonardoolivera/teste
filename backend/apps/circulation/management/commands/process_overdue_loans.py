from django.core.management.base import BaseCommand

from apps.circulation.services import process_overdue_loans


class Command(BaseCommand):
    help = 'Processes overdue loans, recalculates fines, synchronizes automatic patron blocks and sends overdue emails.'

    def handle(self, *args, **options):
        summary = process_overdue_loans()
        self.stdout.write(
            self.style.SUCCESS(
                'Overdue processing complete: '
                f"{summary['loans_marked_overdue']} loans marked overdue, "
                f"{summary['loans_reopened']} loans reopened, "
                f"{summary['patrons_blocked']} patrons blocked, "
                f"{summary['patrons_released']} patrons released, "
                f"{summary['overdue_notifications_sent']} overdue notifications sent."
            )
        )
