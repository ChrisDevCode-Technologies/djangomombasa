from django.urls import path

from . import views

app_name = 'events_and_activities'

urlpatterns = [
    path('events/', views.events, name='events'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
]
