import datetime
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel

class BookedDay(TimeStampedModel):

    """ Booked Days Model Definition """

    day = models.DateField()
    reservation = models.ForeignKey("Reservation", related_name="bookeddays", on_delete=models.CASCADE)

    def __str__(self):
        return str(self.day)
    


class Reservation(TimeStampedModel):

    """Reservation Model Definition"""

    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_CANCELED = "canceled"

    STATUS_CHOICES = (
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_CANCELED, "Canceled"),
    )

    status = models.CharField(
        choices=STATUS_CHOICES, max_length=12, default=STATUS_PENDING
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guest = models.ForeignKey(
        "users.User", related_name="reservations", on_delete=models.CASCADE
    )
    room = models.ForeignKey(
        "rooms.Room", related_name="reservations", on_delete=models.CASCADE
    )

    def __str__(self) -> str:
        return f"{self.room} - {self.check_in}"

    def in_progress(self):
        now = timezone.now().date()
        return now >= self.check_in and now <= self.check_out

    in_progress.boolean = True

    # 만약 체류기간이 지나가면 BookedDay 의 예약을 자동으로 삭제하도록 함
    def is_finished(self):
        now = timezone.now().date()
        is_finished = now > self.check_out
        if is_finished:
            BookedDay.objects.filter(reservation=self).delete()
        return is_finished

    is_finished.boolean = True

    def get_days(self):
        days = self.check_out - self.check_in
        return days


    def save(self, *args, **kwargs):
        if self.pk is None: # 새롭게 생성되는 객체부터 적용
            start = self.check_in
            end = self.check_out
            difference = end - start
            existing_booked_day = BookedDay.objects.filter(day__range=(start, end), reservation__room=self.room).exists()
            if existing_booked_day == False:
                super().save(*args, **kwargs)
                for i in range(difference.days + 1):
                    day = start + datetime.timedelta(days=i)
                    BookedDay.objects.create(day=day, reservation=self)
                return
        return super().save(*args, **kwargs)