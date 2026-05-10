from django.urls import path

from . import views

app_name = 'blog_and_news'

urlpatterns = [
    path('blog/', views.article_list, name='article_list'),
    path('blog/<slug:slug>/', views.article_detail, name='article_detail'),
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),
]
