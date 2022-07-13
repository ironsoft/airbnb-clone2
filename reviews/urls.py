from django.urls import path
from . import views


app_name = "reviews"

urlpatterns = [
    path("create/<int:reservation_pk>/<int:room_pk>/", views.review_create, name="create"),
]
