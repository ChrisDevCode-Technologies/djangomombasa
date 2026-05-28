from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Event, RSVP, ScheduleSlot, SpeakerProposal, Tag, VolunteerSignup


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


class ScheduleSlotResource(resources.ModelResource):
    class Meta:
        model = ScheduleSlot


class ScheduleSlotInline(admin.TabularInline):
    model = ScheduleSlot
    extra = 0
    autocomplete_fields = ('speaker_proposal',)
    fields = ('order', 'title', 'start_time', 'end_time', 'speaker_proposal', 'manual_speaker_name')


@admin.register(Tag)
class TagAdmin(ImportExportModelAdmin):
    resource_classes = [TagResource]
    list_display = ('name',)


@admin.register(Event)
class EventAdmin(ImportExportModelAdmin):
    resource_classes = [EventResource]
    list_display = ('name', 'slug', 'date', 'has_rsvp', 'rsvp_capacity', 'rsvp_deadline', 'has_cfp', 'has_cfv')
    list_filter = ('tags', 'date', 'has_rsvp', 'has_cfp', 'has_cfv')
    search_fields = ('name',)
    filter_horizontal = ('tags',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ScheduleSlotInline]


@admin.register(RSVP)
class RSVPAdmin(ImportExportModelAdmin):
    resource_classes = [RSVPResource]
    list_display = ('event', 'member', 'check_in_status', 'checked_in_at', 'created_at')
    list_filter = ('event', 'check_in_status', 'created_at')
    search_fields = ('event__name', 'member__member_id', 'member__name', 'member__email')
    autocomplete_fields = ('event', 'member')
    readonly_fields = ('check_in_token', 'checked_in_at', 'created_at')


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


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(ImportExportModelAdmin):
    resource_classes = [ScheduleSlotResource]
    list_display = ('event', 'order', 'title', 'start_time', 'end_time', 'speaker_display_name')
    list_filter = ('event',)
    search_fields = ('title', 'event__name', 'manual_speaker_name', 'speaker_proposal__name')
    autocomplete_fields = ('event', 'speaker_proposal')

    @admin.display(description='Speaker')
    def speaker_display_name(self, obj):
        return obj.speaker_display_name or '—'
