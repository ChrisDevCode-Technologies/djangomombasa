from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from .models import Article, NewsItem, Topic

_PAGE_SIZE = 12


def article_list(request):
    qs = Article.published.all()

    topic_slug = request.GET.get('topic')
    active_topic = None
    if topic_slug:
        active_topic = Topic.objects.filter(slug=topic_slug).first()
        if active_topic:
            qs = qs.filter(topics=active_topic)

    page = Paginator(qs, _PAGE_SIZE).get_page(request.GET.get('page'))

    return render(request, 'blog_and_news/article_list.html', {
        'page_obj': page,
        'topics': Topic.objects.filter(articles__published_at__isnull=False).distinct(),
        'active_topic': active_topic,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article.published, slug=slug)
    related = (
        Article.published
        .filter(topics__in=article.topics.all())
        .exclude(pk=article.pk)
        .distinct()[:3]
    )
    return render(request, 'blog_and_news/article_detail.html', {
        'article': article,
        'related': related,
    })


def news_list(request):
    qs = NewsItem.published.all()

    kind = request.GET.get('kind')
    if kind in {NewsItem.Kind.NEWSLETTER, NewsItem.Kind.EVENT_REPORT}:
        qs = qs.filter(kind=kind)

    page = Paginator(qs, _PAGE_SIZE).get_page(request.GET.get('page'))

    return render(request, 'blog_and_news/news_list.html', {
        'page_obj': page,
        'active_kind': kind,
        'kind_choices': NewsItem.Kind.choices,
    })


def news_detail(request, slug):
    news_item = get_object_or_404(NewsItem.published, slug=slug)
    return render(request, 'blog_and_news/news_detail.html', {
        'news_item': news_item,
    })
