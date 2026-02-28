from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import (
    County, InstitutionCategory, InstitutionType, Institution, ParentMinistry,
    ProgrammeGroup, Programme, ProgrammeOffering, DegreeCutoff,
    TvetSection, TvetRequirement,
)


class CountyResource(resources.ModelResource):
    class Meta:
        model = County


class ParentMinistryResource(resources.ModelResource):
    class Meta:
        model = ParentMinistry


class InstitutionCategoryResource(resources.ModelResource):
    class Meta:
        model = InstitutionCategory


class InstitutionTypeResource(resources.ModelResource):
    class Meta:
        model = InstitutionType


class InstitutionResource(resources.ModelResource):
    class Meta:
        model = Institution


@admin.register(County)
class CountyAdmin(ImportExportModelAdmin):
    resource_classes = [CountyResource]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(ParentMinistry)
class ParentMinistryAdmin(ImportExportModelAdmin):
    resource_classes = [ParentMinistryResource]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(InstitutionCategory)
class InstitutionCategoryAdmin(ImportExportModelAdmin):
    resource_classes = [InstitutionCategoryResource]
    list_display = ('name',)


@admin.register(InstitutionType)
class InstitutionTypeAdmin(ImportExportModelAdmin):
    resource_classes = [InstitutionTypeResource]
    list_display = ('name',)


@admin.register(Institution)
class InstitutionAdmin(ImportExportModelAdmin):
    resource_classes = [InstitutionResource]
    list_display = ('kuccps_number', 'code', 'name', 'category', 'institution_type', 'county')
    list_filter = ('category', 'institution_type', 'parent_ministry', 'county')
    search_fields = ('code', 'name')
    list_select_related = ('category', 'institution_type', 'parent_ministry', 'county')


class ProgrammeGroupResource(resources.ModelResource):
    class Meta:
        model = ProgrammeGroup


class ProgrammeResource(resources.ModelResource):
    class Meta:
        model = Programme


class ProgrammeOfferingResource(resources.ModelResource):
    class Meta:
        model = ProgrammeOffering


@admin.register(ProgrammeGroup)
class ProgrammeGroupAdmin(ImportExportModelAdmin):
    resource_classes = [ProgrammeGroupResource]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Programme)
class ProgrammeAdmin(ImportExportModelAdmin):
    resource_classes = [ProgrammeResource]
    list_display = ('kuccps_id', 'name', 'group')
    list_filter = ('group',)
    search_fields = ('kuccps_id', 'name')
    list_select_related = ('group',)


@admin.register(ProgrammeOffering)
class ProgrammeOfferingAdmin(ImportExportModelAdmin):
    resource_classes = [ProgrammeOfferingResource]
    list_display = ('programme_code', 'programme_name', 'get_institution_name', 'get_institution_type', 'cutoff_2025', 'cutoff_2024', 'cutoff_2023')
    list_filter = ('institution__institution_type', 'programme__group')
    search_fields = ('programme_code', 'programme_name', 'institution__name')
    list_select_related = ('programme', 'institution__institution_type')
    raw_id_fields = ('programme', 'institution')

    @admin.display(description='Institution', ordering='institution__name')
    def get_institution_name(self, obj):
        return obj.institution.name

    @admin.display(description='Type', ordering='institution__institution_type__name')
    def get_institution_type(self, obj):
        return obj.institution.institution_type


class DegreeCutoffResource(resources.ModelResource):
    class Meta:
        model = DegreeCutoff


@admin.register(DegreeCutoff)
class DegreeCutoffAdmin(ImportExportModelAdmin):
    resource_classes = [DegreeCutoffResource]
    list_display = (
        'rank', 'category', 'get_programme_name', 'get_institution',
        'cutoff_2024', 'cutoff_2023', 'cutoff_2022', 'cutoff_2021',
        'cutoff_2020', 'cutoff_2019', 'cutoff_2018',
    )
    list_filter = ('category',)
    search_fields = ('category', 'offering__programme_name', 'offering__institution__name')
    list_select_related = ('offering__institution',)
    raw_id_fields = ('offering',)

    @admin.display(description='Programme', ordering='offering__programme_name')
    def get_programme_name(self, obj):
        return obj.offering.programme_name

    @admin.display(description='Institution', ordering='offering__institution__name')
    def get_institution(self, obj):
        return obj.offering.institution.name


class TvetSectionResource(resources.ModelResource):
    class Meta:
        model = TvetSection


class TvetRequirementResource(resources.ModelResource):
    class Meta:
        model = TvetRequirement


@admin.register(TvetSection)
class TvetSectionAdmin(ImportExportModelAdmin):
    resource_classes = [TvetSectionResource]
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TvetRequirement)
class TvetRequirementAdmin(ImportExportModelAdmin):
    resource_classes = [TvetRequirementResource]
    list_display = ('number', 'category', 'subcategory', 'level', 'minimum_mean_grade', 'section')
    list_filter = ('section', 'level', 'category')
    search_fields = ('category', 'subcategory')
    list_select_related = ('section',)
