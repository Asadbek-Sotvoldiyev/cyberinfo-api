from rest_framework import serializers
from .models import NewsCategory, News, Comment


class NewsCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = NewsCategory
        fields = '__all__'


class NewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = News
        fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'news', 'content')

    def to_representation(self, instance):
        data = {
            "user_id": instance.user.id,
            "news_id": instance.news.id,
            'comment_id': instance.id,
            "comment text": instance.content
        }
        return data
