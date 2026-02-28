from django.urls import path

from . import views

app_name = 'kenya_kuccps'

urlpatterns = [
    path('', views.index, name='index'),
    path('maps/', views.maps, name='maps'),
    path('eligibility/', views.eligibility, name='eligibility'),
    path('api/county-stats/', views.county_stats_api, name='county_stats_api'),
    path('api/cluster-county-stats/', views.cluster_county_stats_api, name='cluster_county_stats_api'),
    path('api/eligibility/', views.eligibility_api, name='eligibility_api'),
    path('api/programmes/', views.programmes_list_api, name='programmes_list_api'),
    path('api/programme-requirements/<uuid:pk>/', views.programme_requirements_api, name='programme_requirements_api'),
]
