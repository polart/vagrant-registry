from django.core.management.base import BaseCommand
from apps.boxes.models import BoxUpload


class Command(BaseCommand):
    help = 'Removes expired and completed boxes uploads'

    def handle(self, *args, **options):
        deleted = BoxUpload.objects.not_active().delete()
        self.stdout.write(
            self.style.SUCCESS('Successfully removed {} expired '
                               'and completed uploads.'
                               .format(deleted[0]))
        )
