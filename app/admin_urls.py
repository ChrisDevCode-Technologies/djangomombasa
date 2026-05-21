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
    path('messaging/', admin_views.broadcast, name='broadcast'),
]
