import random
from django.core.management.base import BaseCommand
from django.contrib.admin.utils import flatten
from django_seed import Seed
from rooms.models import Amenity, Facility, HouseRule, Photo, Room, RoomType
from users.models import User


class Command(BaseCommand):

    help = "This command creates rooms."

    def add_arguments(self, parser):
        parser.add_argument(
            "--number",
            type=int,
            default=1,
            help="How many rooms do you want to create?",
        )

    def handle(self, *args, **options):
        numbers = options.get("number")
        all_users = User.objects.all()
        room_type = RoomType.objects.all()
        amenities = Amenity.objects.all()
        facilities = Facility.objects.all()
        house_rules = HouseRule.objects.all()
        seeder = Seed.seeder()
        seeder.add_entity(
            Room,
            numbers,
            {
                "name": lambda x: seeder.faker.address(),
                "host": lambda x: random.choice(all_users),
                "room_type": lambda x: random.choice(room_type),
                "guests": lambda x: random.randint(1, 20),
                "price": lambda x: random.randint(1, 300),
                "beds": lambda x: random.randint(1, 5),
                "bedrooms": lambda x: random.randint(1, 5),
                "baths": lambda x: random.randint(1, 5),
            },
        )
        # 사진의 경우
        created_photo = seeder.execute()
        created_clean = flatten(list(created_photo.values()))
        for pk in created_clean:
            room = Room.objects.get(pk=pk)
            for i in range(3, random.randint(10, 30)):
                Photo.objects.create(
                    caption=seeder.faker.sentence(),
                    image_file=f"room_photos/{random.randint(1, 31)}.webp",
                    room=room,
                )
            # foreign key의 경우에는 choice로 저장할 수 있으나, manytomany의 관계에서는 add를 사용해야 함.
            for a in amenities:
                random_num = random.randint(0, 17)
                if random_num % 2 == 0:
                    room.amenities.add(a)
            for f in facilities:
                random_num = random.randint(0, 17)
                if random_num % 2 == 0:
                    room.facilities.add(f)
            for h in house_rules:
                random_num = random.randint(0, 17)
                if random_num % 2 == 0:
                    room.house_rules.add(h)

        self.stdout.write(self.style.SUCCESS(f"{numbers} Created Successfully!"))
