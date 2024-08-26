from http.client import responses

from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NewsCategorySerializer, NewsSerializer, CommentSerializer
from .models import NewsCategory, News, Comment
from .news_views import NewViews


class NewsCategoryApiView(APIView):
    def get(self, request):
        categories = NewsCategory.objects.all()
        serializer = NewsCategorySerializer(categories, many=True)

        if not categories.exists():
            data = {
                "status": False,
                "Message": "Kategoriyalar mavjud emas!"
            }
            return Response(data, status=404)
        data = {
            "status": True,
            "data": serializer.data
        }
        return Response(data, status=200)


class NewsApiView(APIView):
    def get(self, request):
        news = News.objects.all()
        serializer = NewsSerializer(news, many=True)

        return Response(serializer.data)


class NewDetailApiView(APIView):
    def get(self, request, id):
        new = News.objects.get(id=id)
        serializer = NewsSerializer(new)
        new_view = NewViews(request)
        new_view.add(new)

        return Response(serializer.data)


class AddCommentApiView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data)


class GetAllNewComments(ListAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        news_id = self.kwargs['news_id']
        return Comment.objects.filter(news_id=news_id)


class AllMyCommentsApiView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

