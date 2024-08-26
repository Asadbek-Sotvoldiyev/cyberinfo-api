from django.urls import path
from .views import NewsCategoryApiView, NewsApiView, NewDetailApiView, AddCommentApiView, GetAllNewComments, \
    AllMyCommentsApiView

urlpatterns = [
    path('categories/', NewsCategoryApiView.as_view()),
    path('all-news/', NewsApiView.as_view()),
    path('<int:id>/', NewDetailApiView.as_view()),
    path('add-comment/', AddCommentApiView.as_view()),
    path('get-all-new-comments/<int:news_id>/', GetAllNewComments.as_view()),
    path('all-my-comments/', AllMyCommentsApiView.as_view()),
]
