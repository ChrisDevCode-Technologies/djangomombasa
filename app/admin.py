from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Event, Member, Page, SocialLink, Tag


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag


class EventResource(resources.ModelResource):
    class Meta:
        model = Event


class MemberResource(resources.ModelResource):
    class Meta:
        model = Member


class SocialLinkResource(resources.ModelResource):
    class Meta:
        model = SocialLink


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ('name',)


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_classes = [EventResource]
    list_display = ('name', 'date')
    list_filter = ('tags', 'date')
    filter_horizontal = ('tags',)


@admin.register(Member)
class MemberAdmin(ImportExportModelAdmin):
    resource_classes = [MemberResource]
    list_display = ('member_id', 'name', 'email', 'gender', 'experience_level', 'primary_language', 'joined_at')
    list_filter = ('gender', 'experience_level', 'primary_language')
    search_fields = ('name', 'email')


class PageResource(resources.ModelResource):
    class Meta:
        model = Page


@admin.register(Page)
class PageAdmin(SummernoteModelAdmin, ImportExportModelAdmin):
    resource_classes = [PageResource]
    summernote_fields = ('content',)
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(SocialLink)
class SocialLinkAdmin(ImportExportModelAdmin):
    resource_classes = [SocialLinkResource]
    list_display = ('name', 'url', 'order')
    list_editable = ('order',)
