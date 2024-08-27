from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NewsCategorySerializer, NewsSerializer, CommentSerializer, NewsImageSerializer, \
    NewsContentSerializer
from .models import NewsCategory, News, Comment, NewsImage, ContentSection
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

        if not news.exists():
            data = {
                "status": False,
                "Message": "Yangiliklar mavjud emas!"
            }
            return Response(data, status=404)
        data = {
            "status": True,
            "data": serializer.data
        }
        return Response(data, status=200)


class NewDetailApiView(APIView):
    def get(self, request, id):
        new = News.objects.filter(id=id).first()
        images = NewsImage.objects.filter(news=new)
        contents = ContentSection.objects.filter(news=new)
        new_serializer = NewsSerializer(new)
        image_serializer = NewsImageSerializer(images, many=True)
        content_serializer = NewsContentSerializer(contents, many=True)

        if new is None:
            data = {
                "status": False,
                "message": "New not found"
            }
            return Response(data, 404)

        new_view = NewViews(request)
        new_view.add(new)

        data = {
            "status": True,
            "New": new_serializer.data,
            "Images": image_serializer.data,
            "Contents": content_serializer.data
        }
        return Response(data, status=200)


class AddCommentApiView(APIView):
    permission_classes = (IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CommentSerializer,
        responses={
            201: openapi.Response(
                description='Commented successfully',
                examples={
                    'application/json': {
                        "user_id": "user_id",
                        "news_id": 'news_id',
                        "comment_id": 'comment_id',
                        "comment_text": 'comment_text',
                    }
                }
            ),
            400: openapi.Response(
                description='Validation error',
                examples={
                    'application/json': {
                        'non_field_errors': ['Some error message']
                    }
                }
            )
        }
    )

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

