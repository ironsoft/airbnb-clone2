import random
from django.core.management.base import BaseCommand
from django_seed import Seed
from rooms.models import Room
from users.models import User
from reviews.models import Review


class Command(BaseCommand):

    help = "This command creates reviews."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=1,
            help="How many reviews do you want to create?",
        )

    def handle(self, *args, **options):
        numbers = options.get("number")
        all_users = User.objects.all()
        all_rooms = Room.objects.all()
        seeder = Seed.seeder()
        seeder.add_entity(
            Review,
            numbers,
            {
                "accuracy": lambda x: random.randint(1, 5),
                "communication": lambda x: random.randint(1, 5),
                "cleanliness": lambda x: random.randint(1, 5),
                "location": lambda x: random.randint(1, 5),
                "check_in": lambda x: random.randint(1, 5),
                "value": lambda x: random.randint(1, 5),
                "user": lambda x: random.choice(all_users),
                "room": lambda x: random.choice(all_rooms),
            },
        )
        seeder.execute()
        self.stdout.write(self.style.SUCCESS(f"{numbers} Created Successfully!"))
