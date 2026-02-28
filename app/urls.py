from django.urls import include, path

from . import views

app_name = 'app'

membership_patterns = [
    path('', views.membership, name='membership'),
    path('join/', views.join, name='join'),
    path('join/success/<str:member_id>/', views.join_success, name='join_success'),
    path('join/send-id/<str:member_id>/', views.send_member_id, name='send_member_id'),
    path('lookup/', views.lookup, name='lookup'),
    path('lookup/request-details/<str:member_id>/', views.request_details, name='request_details'),
    path('lookup/request-deletion/<str:member_id>/', views.request_deletion, name='request_deletion'),
]

urlpatterns = [
    path('', views.index, name='index'),
    path('events/', views.events, name='events'),
    path('team/', views.team, name='team'),
    path('membership/', include(membership_patterns)),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
]
