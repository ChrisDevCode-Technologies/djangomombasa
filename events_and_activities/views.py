from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from .models import Event


def events(request):
    upcoming = Event.objects.filter(date__gte=timezone.now())
    past = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'events_and_activities/events.html', {'upcoming': upcoming, 'past': past})


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    return render(request, 'events_and_activities/event_detail.html', {'event': event})
