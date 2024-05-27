from django.contrib import admin
from .models import NewsCategory, News, Comment


admin.site.register([News, NewsCategory, Comment])
