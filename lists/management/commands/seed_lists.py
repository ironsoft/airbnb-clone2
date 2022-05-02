import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms.models import Room
from users.models import User
from lists.models import List


class Command(BaseCommand):

    help = "This command creates lists."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=1,
            help="How many lists do you want to create?",
        )

    def handle(self, *args, **options):
        numbers = options.get("number")
        all_users = User.objects.all()
        all_rooms = Room.objects.all()
        seeder = Seed.seeder()
        seeder.add_entity(
            List,
            numbers,
            {
                "user": lambda x: random.choice(all_users),
            },
        )
        room_num = seeder.execute()
        cleaned_num = flatten(list(room_num.values()))
        for pk in cleaned_num:
            the_list = List.objects.get(pk=pk)
            to_add = all_rooms[random.randint(0, 5) : random.randint(6, 30)]
            the_list.rooms.add(*to_add)

        self.stdout.write(self.style.SUCCESS(f"{numbers} Created Successfully!"))
