from django.db import models


class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Organizer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    community_role = models.CharField(max_length=200, help_text='Role in the Django Mombasa community')
    professional_role = models.CharField(max_length=200, blank=True, help_text='Professional job title')
    location = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='organizers/', blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Partner(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='partners/', blank=True)
    website_url = models.URLField(blank=True)
    events = models.ManyToManyField('events_and_activities.Event', blank=True, related_name='partners')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Sponsor(models.Model):
    class Tier(models.TextChoices):
        PLATINUM = 'platinum', 'Platinum'
        GOLD = 'gold', 'Gold'
        SILVER = 'silver', 'Silver'
        BRONZE = 'bronze', 'Bronze'
        COMMUNITY = 'community', 'Community'

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='sponsors/', blank=True)
    website_url = models.URLField(blank=True)
    tier = models.CharField(max_length=20, choices=Tier.choices, default=Tier.COMMUNITY)
    events = models.ManyToManyField('events_and_activities.Event', blank=True, related_name='sponsors')
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class SocialLink(models.Model):
    name = models.CharField(max_length=50)
    icon_class = models.CharField(max_length=100, help_text='Bootstrap Icons class, e.g. "bi bi-linkedin"')
    url = models.URLField()
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
