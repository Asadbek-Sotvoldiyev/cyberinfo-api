from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .telegram_auth import auth_telegram
import threading

def start_bot():
    threading.Thread(target=auth_telegram).start()

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        post_migrate.connect(start_bot, sender=self)
