from django.urls import path

from . import views

app_name = 'membership'

urlpatterns = [
    path('', views.membership, name='info'),
    path('join/', views.join, name='join'),
    path('join/success/<str:member_id>/', views.join_success, name='join_success'),
    path('join/send-id/<str:member_id>/', views.send_member_id, name='send_member_id'),
    path('lookup/', views.lookup, name='lookup'),
    path('lookup/request-details/<str:member_id>/', views.request_details, name='request_details'),
    path('lookup/request-deletion/<str:member_id>/', views.request_deletion, name='request_deletion'),
]
