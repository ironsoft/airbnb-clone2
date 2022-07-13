from datetime import datetime
from django.forms import forms
from django.http import Http404
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, UpdateView, FormView, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from rooms.models import Amenity, Facility, Photo, Room, RoomType
from django.contrib import messages
from users import mixins as user_mixins
from . import forms


class HomeView(ListView):

    model = Room
    paginate_by = 12
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        now = datetime.now()
        all_rooms = Room.objects.all().count
        context = super().get_context_data(**kwargs)
        context['all_rooms'] = all_rooms
        context["now"] = now
        return context


class RoomDetail(DetailView):

    model = Room


class SearchView(View):

    """Search View Definition"""

    def get(self, request):

        country = request.GET.get("country")

        if country:

            form = forms.SearchForm(request.GET)

            if form.is_valid():
                s_city = form.cleaned_data.get("city")
                s_country = form.cleaned_data.get("country")
                s_room_type = form.cleaned_data.get("room_type")
                s_price = form.cleaned_data.get("price")
                s_guests = form.cleaned_data.get("guests")
                s_beds = form.cleaned_data.get("beds")
                s_bedrooms = form.cleaned_data.get("bedrooms")
                s_baths = form.cleaned_data.get("baths")
                is_instant_book = form.cleaned_data.get("instant_book")
                is_superhost = form.cleaned_data.get("superhost")
                s_amenities = form.cleaned_data.get("amenities")
                s_facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if s_city != "Anywhere":
                    filter_args["city__startswith"] = s_city

                filter_args["country"] = s_country

                if s_room_type is not None:
                    filter_args["room_type__pk"] = s_room_type

                if s_price is not None:
                    filter_args["price__lte"] = s_price

                if s_guests is not None:
                    filter_args["guests__gte"] = s_guests

                if s_beds is not None:
                    filter_args["beds__gte"] = s_beds

                if s_bedrooms is not None:
                    filter_args["bedrooms__gte"] = s_bedrooms

                if s_baths is not None:
                    filter_args["baths__gte"] = s_baths

                if is_instant_book is True:
                    filter_args["instant_book"] = True

                if is_superhost is True:
                    filter_args["host__superhost"] = True

                rooms = Room.objects.filter(**filter_args)

                for s_amenity in s_amenities:
                    rooms = rooms.filter(amenities=s_amenity)

                for s_facility in s_facilities:
                    rooms = rooms.filter(facilities=s_facility)

                qs = rooms.order_by("-created")
                paginator = Paginator(qs, 3, orphans=1)

                page = request.GET.get("page")

                rooms = paginator.get_page(page)

                return render(
                    request,
                    "rooms/search.html",
                    context={
                        "form": form,
                        "rooms": rooms,
                        # "current_url": current_url,
                    },
                )

        form = forms.SearchForm()

        return render(
            request,
            "rooms/search.html",
            {
                "form": form,
            },
        )


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):

    model = Room
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )
    pk_url_kwarg = 'pk'
    template_name = "rooms/edit_room.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

class RoomPhotoView(user_mixins.LoggedInOnlyView, DetailView):

    model = Room
    template_name = "rooms/room_photos.html"
    pk_url_kwarg = 'pk'

    def get_object(self, queryset=None):
        room = super().get_object(queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room

@login_required
def delete_photo(request, room_pk, photo_pk):
    user = request.user
    try:
        # 실제 룸이 있는지 확인한다. 없으면 에러가 발생하기 때문에 try~ except~ 로 작성한다. 
        # 이 룸의 호스트와 로그인한 사람이 같은지 확인한다. 
        # 같으면 photo_pk 의 포토를 모델에서 찾아서 삭제한다. 
        # 그리고 다시 포토 페이지로 돌려 보낸다. 
        # 다르면 삭제할 권한이 없다는 메세지를 보낸다. 
        room = Room.objects.get(pk=room_pk)
        if room.host.pk == user.pk:
            photo = Photo.objects.filter(pk=photo_pk)
            photo.delete()
            messages.success(request, "Photo Deleted!")
        else:
            messages.error(request, "You are not authorized!")
        
        return redirect(reverse('rooms:photos', kwargs={"pk":room_pk}))
            
    except Room.DoesNotExist:
        return redirect(reverse('core:home'))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):

    model = Photo
    fields = ("caption", "image_file",)
    template_name = "rooms/edit_photo.html"
    pk_url_kwarg = 'photo_pk'
    success_message = "Photo Updated"

    def get_success_url(self) -> str:
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk":room_pk})


class UploadPhotoView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.UploadPhotoForm
    template_name = "rooms/upload_photo.html"

    def form_valid(self, form):
        pk = self.kwargs.get("room_pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded!")
        return redirect(reverse("rooms:photos", kwargs={'pk':pk}))



class UploadRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.UploadRoomForm
    template_name = "rooms/upload_room.html"

    def form_valid(self, form):
        room = form.save()
        user = self.request.user
        room.host = user
        room.save()
        form.save_m2m()
        messages.success(self.request, "Room Uploaded!")
        return redirect(reverse("rooms:detail", kwargs={'pk':room.pk}))

def delete_room(request, pk):
    user = request.user
    room = Room.objects.get(pk=pk)
    room.delete()
    messages.success(request, "Room Deleted!")
    return redirect(reverse("users:profile", kwargs={'pk':user.pk}))