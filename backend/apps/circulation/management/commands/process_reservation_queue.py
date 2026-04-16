from django.core.management.base import BaseCommand

from apps.circulation.services import process_expired_reservations


class Command(BaseCommand):
    help = 'Expires reservation holds whose pickup deadline has passed and promotes the next patrons in line.'

    def handle(self, *args, **options):
        summary = process_expired_reservations()
        self.stdout.write(
            self.style.SUCCESS(
                'Reservation queue processing complete: '
                f"{summary['reservations_expired']} reservations expired, "
                f"{summary['reservations_promoted']} reservations promoted, "
                f"{summary['copies_released']} copies released."
            )
        )
