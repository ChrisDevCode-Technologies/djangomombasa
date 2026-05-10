from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Event, RSVP, SpeakerProposal, Tag, VolunteerSignup


class TagResource(resources.ModelResource):
    class Meta:
        model = Tag


class EventResource(resources.ModelResource):
    class Meta:
        model = Event


class RSVPResource(resources.ModelResource):
    class Meta:
        model = RSVP


class SpeakerProposalResource(resources.ModelResource):
    class Meta:
        model = SpeakerProposal


class VolunteerSignupResource(resources.ModelResource):
    class Meta:
        model = VolunteerSignup


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ('name',)


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_classes = [EventResource]
    list_display = ('name', 'slug', 'date', 'has_rsvp', 'has_cfp', 'has_cfv')
    list_filter = ('tags', 'date', 'has_rsvp', 'has_cfp', 'has_cfv')
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(RSVP)
class RSVPAdmin(ImportExportModelAdmin):
    resource_classes = [RSVPResource]
    list_display = ('event', 'member', 'created_at')
    list_filter = ('event', 'created_at')
    search_fields = ('event__name', 'member__member_id', 'member__name', 'member__email')
    autocomplete_fields = ('event', 'member')


@admin.register(SpeakerProposal)
class SpeakerProposalAdmin(ImportExportModelAdmin):
    resource_classes = [SpeakerProposalResource]
    list_display = ('name', 'email', 'event', 'proposed_talk_title', 'status', 'submitted_at')
    list_filter = ('status', 'event', 'submitted_at')
    search_fields = ('name', 'email', 'proposed_talk_title', 'event__name')
    list_editable = ('status',)
    autocomplete_fields = ('event',)


@admin.register(VolunteerSignup)
class VolunteerSignupAdmin(ImportExportModelAdmin):
    resource_classes = [VolunteerSignupResource]
    list_display = ('name', 'email', 'event', 'skills_or_role', 'status', 'submitted_at')
    list_filter = ('status', 'event', 'submitted_at')
    search_fields = ('name', 'email', 'skills_or_role', 'event__name')
    list_editable = ('status',)
    autocomplete_fields = ('event',)
