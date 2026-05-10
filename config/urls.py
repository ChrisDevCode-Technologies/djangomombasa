from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('app.urls')),
    path('', include('events_and_activities.urls')),
    path('', include('blog_and_news.urls')),
    path('membership/', include('membership.urls')),
    path('dashboard/', admin.site.urls),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
