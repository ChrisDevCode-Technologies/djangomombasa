from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Event, Tag


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag


class EventResource(resources.ModelResource):
    class Meta:
        model = Event


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ('name',)


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_classes = [EventResource]
    list_display = ('name', 'slug', 'date')
    list_filter = ('tags', 'date')
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('name',)}
