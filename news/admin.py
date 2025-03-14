from django.contrib import admin
from .models import NewsCategory, News, Comment, ContentSection


admin.site.register([News, NewsCategory, Comment, ContentSection])
