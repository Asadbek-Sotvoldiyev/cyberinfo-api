from django.urls import path
from .views import GetVideoApiView

urlpatterns = [
    path('', GetVideoApiView.as_view()),
]