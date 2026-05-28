from django.urls import path

from . import admin_views

app_name = 'custom_admin'

urlpatterns = [
    path('', admin_views.dashboard, name='dashboard'),
    path('login/', admin_views.admin_login, name='admin_login'),
    path('logout/', admin_views.admin_logout, name='admin_logout'),
    path('events/', admin_views.event_list, name='event_list'),
    path('events/new/', admin_views.event_create, name='event_create'),
    path('events/<slug:slug>/', admin_views.event_detail, name='event_detail'),
    path('events/<slug:slug>/edit/', admin_views.event_edit, name='event_edit'),
    path('members/', admin_views.member_list, name='member_list'),
    path('members/new/', admin_views.member_create, name='member_create'),
    path('members/<str:member_id>/', admin_views.member_detail, name='member_detail'),
    path('members/<str:member_id>/edit/', admin_views.member_edit, name='member_edit'),
    path('proposals/<int:pk>/status/', admin_views.speaker_proposal_status, name='speaker_proposal_status'),
    path('volunteers/<int:pk>/status/', admin_views.volunteer_signup_status, name='volunteer_signup_status'),
    path('events/<slug:slug>/check-in/', admin_views.event_check_in, name='event_check_in'),
    path('rsvps/<int:pk>/check-in-status/', admin_views.rsvp_check_in_status, name='rsvp_check_in_status'),
    path('events/<slug:slug>/schedule/new/', admin_views.schedule_slot_create, name='schedule_slot_create'),
    path('schedule/<int:pk>/edit/', admin_views.schedule_slot_edit, name='schedule_slot_edit'),
    path('schedule/<int:pk>/delete/', admin_views.schedule_slot_delete, name='schedule_slot_delete'),
    path('messaging/', admin_views.broadcast, name='broadcast'),
]
