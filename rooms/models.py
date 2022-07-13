from django.utils import timezone
from django.db import models
from django.urls import reverse
from django_countries.fields import CountryField
from core.models import TimeStampedModel
from cal import Calendar

class AbstractItem(TimeStampedModel):

    """Abstract Item Model"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True  # DB에 테이블을 저장하지 않고 이름을 생성해 주는 기능

    def __str__(self) -> str:
        return self.name


class RoomType(AbstractItem):

    """Room Type Model Definition"""

    class Meta:
        verbose_name = "Room Type"


class Amenity(AbstractItem):

    """Amenity Model Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):

    """Facility Model Definition"""

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):

    """House Rule Model Definition"""

    class Meta:
        verbose_name = "House Rule"


class Photo(TimeStampedModel):

    """Photo Model Definition"""

    caption = models.CharField(max_length=80)
    image_file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey(
        "Room", related_name="photos", on_delete=models.CASCADE
    )  # 위에서 부터 순차적으로 코드를 읽기에 Room을 찾지 못함. 그래서 "Room" 사용.

    def __str__(self) -> str:
        return self.caption


class Room(TimeStampedModel):

    """Room Model Definition"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField(help_text="How many guests will be staying?")
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    host = models.ForeignKey(
        "users.User", related_name="rooms", on_delete=models.CASCADE
    )
    room_type = models.ForeignKey(
        "RoomType", related_name="rooms", on_delete=models.SET_NULL, null=True
    )
    amenities = models.ManyToManyField("Amenity", related_name="rooms", blank=True)
    facilities = models.ManyToManyField("Facility", related_name="rooms", blank=True)
    house_rules = models.ManyToManyField("HouseRule", related_name="rooms", blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})


    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0
        if len(all_reviews) > 0:
            for review in all_reviews:
                all_ratings += review.rating_average()
                avg = all_ratings / len(all_reviews)
                return round(avg, 2)
        else:
            return 0
    
    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save(*args, **kwargs)  # Call the real save() method
    
    def first_photo(self):
        try:
            photo, = self.photos.all()[:1] 
            # photo로 받으면 1개만 받아도 queryset으로 받기 때문에 한꺼풀 더 벗겨내야함. 그래서 python의 특성인 ,를 사용하면 배열안에 요소를 한씩 받아내기에 photo, 를 사용함.
            return photo.image_file.url
        except ValueError:
            return None

    def get_next_four_photos(self):
        photos = self.photos.all()[1:5]
        return photos

    def get_calendar(self):
        now = timezone.now()
        currentYear = now.year
        nextYear = currentYear
        currentMonth = now.month
        nextMonth = currentMonth + 1
        if nextMonth == 13: # 만약 다음달이 13월이 되면 해가 바뀐다는 뜻이므로.
            nextMonth = 1
            nextYear = nextYear + 1
        this_month = Calendar(currentYear, currentMonth)
        next_month = Calendar(nextYear, nextMonth)
        return [this_month, next_month]