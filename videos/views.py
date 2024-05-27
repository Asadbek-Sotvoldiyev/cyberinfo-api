from .models import UsefulVideo
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UsefulVideoSerializer


class GetVideoApiView(APIView):
    def get(self, request):
        videos = UsefulVideo.objects.all()
        serializer = UsefulVideoSerializer(videos, many=True)

        return Response(serializer.data)

