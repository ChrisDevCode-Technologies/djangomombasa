from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Event, Member, Organizer, Page, Partner, SocialLink, Sponsor, Tag


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
    list_display = ('name', 'slug', 'date')
    list_filter = ('tags', 'date')
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Member)
class MemberAdmin(ImportExportModelAdmin):
    resource_classes = [MemberResource]
    list_display = ('member_id', 'name', 'email', 'gender', 'experience_level', 'primary_language', 'receive_regular_updates', 'receive_email_communications', 'joined_at')
    list_filter = ('gender', 'experience_level', 'primary_language', 'receive_regular_updates', 'receive_email_communications')
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


class OrganizerResource(resources.ModelResource):
    class Meta:
        model = Organizer


@admin.register(Organizer)
class OrganizerAdmin(ImportExportModelAdmin):
    resource_classes = [OrganizerResource]
    list_display = ('first_name', 'last_name', 'community_role', 'professional_role', 'location', 'order')
    list_editable = ('order',)
    search_fields = ('first_name', 'last_name', 'community_role')


class PartnerResource(resources.ModelResource):
    class Meta:
        model = Partner


@admin.register(Partner)
class PartnerAdmin(ImportExportModelAdmin):
    resource_classes = [PartnerResource]
    list_display = ('name', 'website_url', 'order')
    list_editable = ('order',)
    search_fields = ('name',)
    filter_horizontal = ('events',)


class SponsorResource(resources.ModelResource):
    class Meta:
        model = Sponsor


@admin.register(Sponsor)
class SponsorAdmin(ImportExportModelAdmin):
    resource_classes = [SponsorResource]
    list_display = ('name', 'tier', 'website_url', 'order')
    list_editable = ('order',)
    list_filter = ('tier',)
    search_fields = ('name',)
    filter_horizontal = ('events',)


@admin.register(SocialLink)
class SocialLinkAdmin(ImportExportModelAdmin):
    resource_classes = [SocialLinkResource]
    list_display = ('name', 'url', 'order')
    list_editable = ('order',)
