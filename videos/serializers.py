from rest_framework import serializers
from .models import UsefulVideo


class UsefulVideoSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsefulVideo
        fields = ('id', 'url', 'image')
