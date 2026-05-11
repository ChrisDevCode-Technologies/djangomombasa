from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.text import slugify


def _ensure_unique_slug(model_cls, instance, source_value):
    base = slugify(source_value)
    slug = base or 'untitled'
    n = 1
    while model_cls.objects.filter(slug=slug).exclude(pk=instance.pk).exists():
        slug = f'{base}-{n}'
        n += 1
    return slug


class Topic(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _ensure_unique_slug(Topic, self, self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PublishedManager(models.Manager):
    """Returns posts whose `published_at` is set and not in the future."""

    def get_queryset(self):
        return super().get_queryset().filter(published_at__lte=timezone.now())


class Article(models.Model):
    class Category(models.TextChoices):
        ARTICLE = 'article', 'Article'
        GUIDE = 'guide', 'Technical Guide'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=10, choices=Category.choices, default=Category.ARTICLE)
    author = models.ForeignKey(
        'app.Organizer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
    )
    topics = models.ManyToManyField(Topic, blank=True, related_name='articles')
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to='blog/', blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _ensure_unique_slug(Article, self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class NewsItem(models.Model):
    class Kind(models.TextChoices):
        NEWSLETTER = 'newsletter', 'Newsletter'
        EVENT_REPORT = 'event_report', 'Event Report'

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    kind = models.CharField(max_length=20, choices=Kind.choices, default=Kind.NEWSLETTER)
    event = models.ForeignKey(
        'events_and_activities.Event',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='news_items',
    )
    issue_number = models.PositiveIntegerField(null=True, blank=True)
    topics = models.ManyToManyField(Topic, blank=True, related_name='news_items')
    summary = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to='news/', blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-published_at', '-created_at']

    def clean(self):
        super().clean()
        if self.kind == self.Kind.EVENT_REPORT and self.event_id is None:
            raise ValidationError({'event': 'Event reports must reference an event.'})
        if self.kind == self.Kind.NEWSLETTER and self.event_id is not None:
            raise ValidationError({'event': 'Newsletters should not reference an event.'})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _ensure_unique_slug(NewsItem, self, self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
