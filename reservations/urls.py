from django.urls import path
from . import views

app_name = "reservations"

urlpatterns = [
    path("create/<int:room_pk>/<int:year>-<int:month>-<int:date>", views.create_reservation, name="create"),
    path("detail/<int:pk>/", views.ReservationDetailView.as_view(), name="detail"),
    path("list/<int:room_pk>", views.ReservationListView.as_view(), name="list"),
    path("edit/<int:pk>/<str:verb>", views.edit_reservation, name="edit"),
]
