from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):

    help = "This command creates superuser."

    def handle(self, *args, **options):
        try:
            User.objects.get(username="ebadmin")
            self.stdout.write(self.style.SUCCESS("Superuser already Existed!"))
        except User.DoesNotExist:
            User.objects.create_superuser("ebadmin", "ishopfloor@ishopfloor.com", "123456")
            self.stdout.write(self.style.SUCCESS("Superuser Created!"))
