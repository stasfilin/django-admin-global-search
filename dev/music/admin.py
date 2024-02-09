from django.contrib import admin
from .models import Artist, Album, Song


def get_list_display(model):
    exclude_fields = ["id"]
    return [
        field.name
        for field in model._meta.get_fields()
        if field.name not in exclude_fields
        and not field.many_to_many
        and not field.one_to_many
    ]


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = get_list_display(Artist)


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = get_list_display(Album)


@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = get_list_display(Song)
