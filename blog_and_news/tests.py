from datetime import timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from app.models import Organizer
from events_and_activities.models import Event

from .models import Article, NewsItem, Topic


def _make_event():
    return Event.objects.create(
        name='Meetup #1',
        date=timezone.now() + timedelta(days=7),
        details='See you there.',
    )


def _make_organizer():
    return Organizer.objects.create(
        first_name='Ada',
        last_name='Lovelace',
        community_role='Organizer',
    )


class TopicSlugTest(TestCase):
    def test_slug_auto_filled_from_name(self):
        topic = Topic.objects.create(name='Django ORM')
        self.assertEqual(topic.slug, 'django-orm')

    def test_explicit_slug_kept(self):
        topic = Topic.objects.create(name='Career', slug='careers')
        self.assertEqual(topic.slug, 'careers')


class ArticleSlugTest(TestCase):
    def test_slug_auto_filled(self):
        article = Article.objects.create(title='Getting Started', body='Body.')
        self.assertEqual(article.slug, 'getting-started')

    def test_duplicate_titles_get_suffixed_slug(self):
        a = Article.objects.create(title='Same Title', body='1')
        b = Article.objects.create(title='Same Title', body='2')
        self.assertEqual(a.slug, 'same-title')
        self.assertEqual(b.slug, 'same-title-1')


class NewsItemSlugTest(TestCase):
    def test_slug_auto_filled(self):
        item = NewsItem.objects.create(title='Issue #1', body='Hi', kind=NewsItem.Kind.NEWSLETTER)
        self.assertEqual(item.slug, 'issue-1')


class PublishedManagerTest(TestCase):
    def test_excludes_drafts_and_future_posts(self):
        now = timezone.now()
        live = Article.objects.create(title='Live', body='b', published_at=now - timedelta(hours=1))
        Article.objects.create(title='Draft', body='b', published_at=None)
        Article.objects.create(title='Future', body='b', published_at=now + timedelta(days=1))

        published_ids = list(Article.published.values_list('id', flat=True))
        self.assertEqual(published_ids, [live.id])

    def test_ordering_newest_first(self):
        now = timezone.now()
        older = Article.objects.create(title='Older', body='b', published_at=now - timedelta(days=2))
        newer = Article.objects.create(title='Newer', body='b', published_at=now - timedelta(hours=1))

        ordered = list(Article.published.values_list('id', flat=True))
        self.assertEqual(ordered, [newer.id, older.id])


class NewsItemCleanTest(TestCase):
    def test_event_report_requires_event(self):
        item = NewsItem(title='Recap', body='b', kind=NewsItem.Kind.EVENT_REPORT, event=None)
        with self.assertRaises(ValidationError):
            item.full_clean(exclude=['slug'])

    def test_event_report_with_event_is_valid(self):
        event = _make_event()
        item = NewsItem(title='Recap', body='b', kind=NewsItem.Kind.EVENT_REPORT, event=event)
        item.full_clean(exclude=['slug'])  # should not raise

    def test_newsletter_rejects_event(self):
        event = _make_event()
        item = NewsItem(title='Issue', body='b', kind=NewsItem.Kind.NEWSLETTER, event=event)
        with self.assertRaises(ValidationError):
            item.full_clean(exclude=['slug'])


class ListViewSmokeTest(TestCase):
    def test_article_list_shows_published_and_hides_drafts(self):
        Article.objects.create(title='Live Post', body='b', published_at=timezone.now() - timedelta(hours=1))
        Article.objects.create(title='Hidden Draft', body='b', published_at=None)

        resp = self.client.get(reverse('blog_and_news:article_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Live Post')
        self.assertNotContains(resp, 'Hidden Draft')

    def test_news_list_filters_by_kind(self):
        event = _make_event()
        NewsItem.objects.create(title='Newsletter A', body='b', kind=NewsItem.Kind.NEWSLETTER, published_at=timezone.now() - timedelta(hours=1))
        NewsItem.objects.create(title='Recap A', body='b', kind=NewsItem.Kind.EVENT_REPORT, event=event, published_at=timezone.now() - timedelta(hours=1))

        resp = self.client.get(reverse('blog_and_news:news_list'), {'kind': 'newsletter'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Newsletter A')
        self.assertNotContains(resp, 'Recap A')

    def test_article_detail_returns_200_for_published(self):
        article = Article.objects.create(title='Visible', body='Body.', published_at=timezone.now() - timedelta(hours=1))
        resp = self.client.get(reverse('blog_and_news:article_detail', args=[article.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Visible')

    def test_article_detail_404s_for_draft(self):
        article = Article.objects.create(title='Draft', body='Body.', published_at=None)
        resp = self.client.get(reverse('blog_and_news:article_detail', args=[article.slug]))
        self.assertEqual(resp.status_code, 404)
