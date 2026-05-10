from django.shortcuts import get_object_or_404, render

from .models import Organizer, Page


def index(request):
    return render(request, 'index.html')


def team(request):
    organizers = Organizer.objects.all()
    return render(request, 'team.html', {'organizers': organizers})


def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'page.html', {'page': page})


def list_apps(request):
    return render(request, 'app/list_apps.html')
