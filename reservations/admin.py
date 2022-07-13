from operator import mod
from tabnanny import verbose
from django.contrib import admin
from . import models


@admin.register(models.BookedDay)
class BookedDayAdmin(admin.ModelAdmin):

    """ Booked Days Admin """
    # 노마드를 따라서 치기는 했지만 원리적으로 이건 필요가 없음. 
    class Meta:
        verbose_name = "Booked Day"
        verbose_name_plural = "Booked Days"
    
    list_display = ("day", "reservation")


@admin.register(models.Reservation)
class ReservationAdmin(admin.ModelAdmin):

    """Reservation Admin Definition"""

    list_display = (
        "room",
        "guest",
        "check_in",
        "check_out",
        "status",
        "in_progress",
        "is_finished",
    )

    list_filter = ("status",)
