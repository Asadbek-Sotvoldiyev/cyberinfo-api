from django.contrib import admin
from .models import NewsCategory, News, Comment, NewsImage, ContentSection


admin.site.register([News, NewsCategory, Comment, NewsImage, ContentSection])
