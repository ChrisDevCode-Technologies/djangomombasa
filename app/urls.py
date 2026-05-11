from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path('', views.index, name='index'),
    path('team/', views.team, name='team'),
    path('apps/', views.list_apps, name='list_apps'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
]
