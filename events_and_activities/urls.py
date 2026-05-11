from django.urls import path

from . import views

app_name = 'events_and_activities'

urlpatterns = [
    path('events/', views.events, name='events'),
    path('event/<slug:slug>/', views.event_detail, name='event_detail'),
    path('event/<slug:slug>/rsvp/', views.rsvp, name='event_rsvp'),
    path('event/<slug:slug>/rsvp/success/<int:rsvp_id>/', views.rsvp_success, name='event_rsvp_success'),
    path('event/<slug:slug>/call-for-speakers/', views.call_for_speakers, name='event_cfs'),
    path('event/<slug:slug>/call-for-speakers/thanks/', views.cfp_thank_you, name='event_cfs_thanks'),
    path('event/<slug:slug>/call-for-volunteers/', views.call_for_volunteers, name='event_cfv'),
    path('event/<slug:slug>/call-for-volunteers/thanks/', views.cfv_thank_you, name='event_cfv_thanks'),
]
