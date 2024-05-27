from django.db import models
from shared.models import BaseModel


class UsefulVideo(BaseModel, models.Model):
    url = models.URLField(null=True, blank=True)
    image = models.ImageField(upload_to='video_images/', null=True, blank=True)
