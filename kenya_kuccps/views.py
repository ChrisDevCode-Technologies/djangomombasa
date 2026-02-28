from django.shortcuts import render

from .models import (
    County, Institution, Programme, ProgrammeGroup,
    ProgrammeOffering, DegreeCutoff, TvetSection, TvetRequirement,
)


def index(request):
    """KUCCPS project landing page with dataset stats and feature links."""
    stats = {
        'institutions': Institution.objects.count(),
        'counties': County.objects.count(),
        'programmes': Programme.objects.count(),
        'programme_groups': ProgrammeGroup.objects.count(),
        'offerings': ProgrammeOffering.objects.count(),
        'degree_cutoffs': DegreeCutoff.objects.count(),
        'tvet_sections': TvetSection.objects.count(),
        'tvet_requirements': TvetRequirement.objects.count(),
    }
    return render(request, 'kenya_kuccps/index.html', {'stats': stats})
