from django.db import models
from . import managers

class TimeStampedModel(models.Model):

    """Time Stamped Model Definition"""

    created = models.DateTimeField(
        auto_now_add=True
    )  # auto_now_add=True 모델이 생성되는 날짜와 시간을 기록해 줌
    updated = models.DateTimeField(
        auto_now=True
    )  # auto_now=True 모델이 업데이트 되는 날짜와 시간을 기록해 줌
    objects = managers.CustomReservationManager()

    class Meta:  # abstract해서 DB에 저장되지 않도록 함.
        abstract = True
