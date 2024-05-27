from django.db import models
from shared.models import BaseModel
from users.models import User


class NewsCategory(BaseModel, models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class News(BaseModel, models.Model):
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='news_images/', null=True, blank=True)
    content = models.TextField()
    source = models.CharField(max_length=255)
    views = models.IntegerField(default=0)
    news_category = models.ForeignKey(NewsCategory, on_delete=models.CASCADE, related_name='news')

    def __str__(self):
        return self.title


class Comment(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()

    def __str__(self):
        return f"{self.user.username} commented to {self.news.title}"
