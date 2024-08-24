from django.core.management.base import BaseCommand
from users.telegram_auth import auth_telegram

class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def handle(self, *args, **kwargs):
        auth_telegram()
