from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import Article, NewsItem, Topic


class TopicResource(resources.ModelResource):
    class Meta:
        model = Topic


class ArticleResource(resources.ModelResource):
    class Meta:
        model = Article


class NewsItemResource(resources.ModelResource):
    class Meta:
        model = NewsItem


@admin.register(Topic)
class TopicAdmin(ImportExportModelAdmin):
    resource_classes = [TopicResource]
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin, ImportExportModelAdmin):
    resource_classes = [ArticleResource]
    summernote_fields = ('body',)
    list_display = ('title', 'category', 'author', 'published_at', 'updated_at')
    list_filter = ('category', 'published_at', 'topics')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('topics',)
    autocomplete_fields = ('author',)

    class Media:
        css = {'all': ('css/admin_wide_summernote.css',)}


@admin.register(NewsItem)
class NewsItemAdmin(SummernoteModelAdmin, ImportExportModelAdmin):
    resource_classes = [NewsItemResource]
    summernote_fields = ('body',)
    list_display = ('title', 'kind', 'event', 'issue_number', 'published_at')
    list_filter = ('kind', 'published_at', 'topics')
    search_fields = ('title', 'summary', 'body')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('topics',)
    autocomplete_fields = ('event',)

    class Media:
        css = {'all': ('css/admin_wide_summernote.css',)}
