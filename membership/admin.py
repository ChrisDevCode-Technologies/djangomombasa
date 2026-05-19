from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Member, RSVPGuest


class MemberResource(resources.ModelResource):
    class Meta:
        model = Member


@admin.register(Member)
class MemberAdmin(ImportExportModelAdmin):
    resource_classes = [MemberResource]
    list_display = ('member_id', 'name', 'email', 'gender', 'experience_level', 'primary_language', 'receive_regular_updates', 'receive_email_communications', 'joined_at')
    list_filter = ('kind', 'gender', 'experience_level', 'primary_language', 'receive_regular_updates', 'receive_email_communications')
    search_fields = ('name', 'email')

    def get_queryset(self, request):
        return super().get_queryset(request).filter(kind=Member.Kind.MEMBER)


class RSVPGuestResource(resources.ModelResource):
    class Meta:
        model = RSVPGuest


@admin.register(RSVPGuest)
class RSVPGuestAdmin(ImportExportModelAdmin):
    resource_classes = [RSVPGuestResource]
    list_display = ('member_id', 'name', 'email', 'receive_email_communications', 'joined_at')
    list_filter = ('receive_email_communications', 'joined_at')
    search_fields = ('name', 'email', 'member_id')
