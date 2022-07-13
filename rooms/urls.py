from django.urls import path
from . import views


app_name = "rooms"

urlpatterns = [
    path("<int:pk>/", views.RoomDetail.as_view(), name="detail"),
    path("upload-room/", views.UploadRoomView.as_view(), name="upload-room"),
    path("<int:pk>/edit/", views.EditRoomView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.delete_room, name="delete"),
    path("<int:pk>/photos", views.RoomPhotoView.as_view(), name="photos"),
    path("<int:room_pk>/photos/<int:photo_pk>/edit/", views.EditPhotoView.as_view(), name="edit-photo"),
    path("<int:room_pk>/photos/upload/", views.UploadPhotoView.as_view(), name="upload-photo"),
    path("<int:room_pk>/photos/<int:photo_pk>/delete/", views.delete_photo, name="delete-photo"),
    path("search/", views.SearchView.as_view(), name="search"),
]
