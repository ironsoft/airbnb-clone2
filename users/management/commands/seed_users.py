from django.core.management.base import BaseCommand
from django_seed import Seed
from users.models import User


class Command(BaseCommand):

    help = "This command creates users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=1,
            help="How many users do you want to create?",
        )

    def handle(self, *args, **options):
        numbers = options.get("number")

        seeder = Seed.seeder()
        seeder.add_entity(User, numbers, {"is_staff": False, "is_superuser": False})
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{numbers} Created Successfully!"))
