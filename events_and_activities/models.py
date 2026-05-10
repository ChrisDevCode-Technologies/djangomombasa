from django.db import models
from django.utils.text import slugify


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'app_tag'

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='events')
    date = models.DateTimeField()
    rsvp_link = models.URLField(blank=True)
    details = models.TextField()

    class Meta:
        db_table = 'app_event'
        ordering = ['date']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            n = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
