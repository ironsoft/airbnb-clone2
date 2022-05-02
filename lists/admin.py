from django.contrib import admin
from . import models


@admin.register(models.List)
class ListAdmin(admin.ModelAdmin):

    """List Admin Definition"""

    list_display = (
        "__str__",
        "user",
        "count_rooms",
    )

    search_field = ("name",)

    filter_horizontal = ("rooms",)
