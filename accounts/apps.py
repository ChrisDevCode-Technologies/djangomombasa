from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import post_migrate


def create_dev_superuser(sender, **kwargs):
    if not settings.DEBUG:
        return
    from django.contrib.auth import get_user_model

    User = get_user_model()
    email = 'admin@mail.com'
    if not User.objects.filter(email=email).exists():
        User.objects.create_superuser(email=email, password='123')


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        post_migrate.connect(create_dev_superuser, sender=self)
