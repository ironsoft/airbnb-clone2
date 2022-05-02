from django.contrib import admin
from django.utils.safestring import mark_safe
from . import models

# 룸 사진 파일 기능을 RoomAdmin 안에 삽입하는 방법.
class PhotoInline(admin.TabularInline):

    model = models.Photo


@admin.register(models.Room)
class RoomAdmin(admin.ModelAdmin):

    """Room Admin Definition"""

    inlines = (PhotoInline,)

    fieldsets = (
        (
            "Basic Info",
            {
                "fields": (
                    "name",
                    "description",
                    "country",
                    "city",
                    "address",
                    "price",
                    "room_type",
                )
            },
        ),
        (
            "Times",
            {"fields": ("check_in", "check_out", "instant_book")},
        ),
        ("Spaces", {"fields": ("guests", "beds", "bedrooms", "baths")}),
        (
            "More about the space",
            {
                # "classes": ("collapse",),
                "fields": ("amenities", "facilities", "house_rules"),
            },
        ),
        (
            "Last Details",
            {
                "fields": ("host",),
            },
        ),
    )

    list_display = (
        "name",
        "country",
        "city",
        "price",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "host",
        "room_type",
        "amenities_count",
        "photos_count",
        "total_rating",
    )

    def amenities_count(self, obj):
        return obj.amenities.count()

    amenities_count.short_description = "아메니티 갯수"

    def photos_count(self, obj):
        return obj.photos.count()

    list_filter = (
        "instant_book",
        "host__superhost",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
        "city",
        "country",
    )

    search_fields = (
        "name",
        "=city",
        "^host__username",
    )

    # ManytoMany 필드의 경우만 해당 admin에서 UI 보다 편리하게 변경함.
    filter_horizontal = (
        "amenities",
        "facilities",
        "house_rules",
    )

    # user가 많을 때 검색을 통해 찾을 수 있도록 변경함.
    raw_id_fields = ("host",)


@admin.register(models.RoomType, models.Facility, models.Amenity, models.HouseRule)
class ItemAdmin(admin.ModelAdmin):

    list_display = ("name", "used_by")

    def used_by(self, obj):
        return obj.rooms.count()


@admin.register(models.Photo)
class PhotoAdmin(admin.ModelAdmin):

    """Photo Admin Definition"""

    list_display = ("__str__", "get_thumbnail")

    def get_thumbnail(self, obj):
        return mark_safe(f'<img width="50px" src="{obj.image_file.url}" />')

    get_thumbnail.short_description = "Thumbnail"
