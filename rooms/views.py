from datetime import datetime
from django.forms import forms
from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView
from rooms.models import Amenity, Facility, Room, RoomType
from . import forms


class HomeView(ListView):

    model = Room
    paginate_by = 10
    paginate_orphans = 5
    ordering = "created"
    context_object_name = "rooms"

    def get_context_data(self, **kwargs):
        now = datetime.now()
        context = super().get_context_data(**kwargs)
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
                print(form.cleaned_data)
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

                for s_amenity in s_amenities:
                    filter_args["amenities"] = s_amenity

                for s_facility in s_facilities:
                    filter_args["facilities"] = s_facility

                rooms = Room.objects.filter(**filter_args)

                return render(
                    request,
                    "rooms/search.html",
                    context={"form": form, "rooms": rooms},
                )

        form = forms.SearchForm()

        return render(
            request,
            "rooms/search.html",
            {
                "form": form,
            },
        )


# def search(request):
#     city = request.GET.get("city", "Anywhere")
#     city = str.capitalize(city)
#     s_country = request.GET.get("country", "KR")
#     s_room_type = int(request.GET.get("room_type", 0))
#     s_price = int(request.GET.get("price", 0))
#     s_guests = int(request.GET.get("guests", 0))
#     s_beds = int(request.GET.get("beds", 0))
#     s_bedrooms = int(request.GET.get("bedrooms", 0))
#     s_baths = int(request.GET.get("baths", 0))
#     s_amenities = request.GET.getlist("amenities")  # 복수를 받을 때는 getlist를 써야함.
#     s_facilities = request.GET.getlist("facilities")  # 복수를 받을 때는 getlist를 써야함.
#     is_superhost = bool(request.GET.get("superhost", False))
#     is_instant_book = bool(request.GET.get("instant_book", False))
#     room_types = RoomType.objects.all()
#     amenities = Amenity.objects.all()
#     facilities = Facility.objects.all()

#     form = {
#         "city": city,
#         "s_country": s_country,
#         "s_room_type": s_room_type,
#         "s_price": s_price,
#         "s_guests": s_guests,
#         "s_beds": s_beds,
#         "s_bedrooms": s_bedrooms,
#         "s_baths": s_baths,
#         "s_amenities": s_amenities,
#         "s_facilities": s_facilities,
#         "is_superhost": is_superhost,
#         "is_instant_book": is_instant_book,
#     }

#     choices = {
#         "room_types": room_types,
#         "countries": countries,
#         "amenities": amenities,
#         "facilities": facilities,
#     }

#     filter_args = {}
#     if city != "Anywhere":
#         filter_args["city__startswith"] = city

#     filter_args["country"] = s_country

#     if s_room_type != 0:
#         filter_args["room_type__pk"] = s_room_type

#     if s_price != 0:
#         filter_args["price__lte"] = s_price

#     if s_guests != 0:
#         filter_args["guests__gte"] = s_guests

#     if s_beds != 0:
#         filter_args["beds__gte"] = s_beds

#     if s_bedrooms != 0:
#         filter_args["bedrooms__gte"] = s_bedrooms

#     if s_baths != 0:
#         filter_args["baths__gte"] = s_baths

#     print(s_amenities)
#     if len(s_amenities) > 0:
#         for s_amenity in s_amenities:
#             filter_args["amenities__pk"] = int(s_amenity)

#     if len(s_facilities) > 0:
#         for s_facility in s_facilities:
#             filter_args["facilities__pk"] = int(s_facility)

#     rooms = Room.objects.filter(**filter_args)

#     return render(
#         request,
#         "rooms/search.html",
#         context={**form, **choices, "rooms": rooms},
#     )
