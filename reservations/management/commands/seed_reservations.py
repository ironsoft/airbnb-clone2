import random
from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from django_seed import Seed
from rooms.models import Room
from users.models import User
from reservations.models import Reservastion

NAME = "reservations"


class Command(BaseCommand):

    help = f"This command creates {NAME}."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=1,
            help=f"How many {NAME} do you want to create?",
        )

    def handle(self, *args, **options):
        numbers = options.get("number")
        all_users = User.objects.all()
        all_rooms = Room.objects.all()
        seeder = Seed.seeder()
        seeder.add_entity(
            Reservastion,
            numbers,
            {
                "status": lambda x: random.choice(["pending", "confirmed", "canceled"]),
                "guest": lambda x: random.choice(all_users),
                "room": lambda x: random.choice(all_rooms),
                "check_in": lambda x: datetime.now(),
                "check_out": lambda x: datetime.now()
                + timedelta(days=random.randint(3, 30)),
            },
        )
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{numbers} {NAME} Created Successfully!"))
