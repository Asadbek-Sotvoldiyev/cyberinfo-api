from datetime import datetime

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView, UpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from shared.utils import send_email
from users.models import User, DONE, CODE_VERIFIED
from users.serializers import SignUpSerializer, ChangeUserInformation, LoginSerializer, CodeSerializer


class CreateUserView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny, )
    serializer_class = SignUpSerializer


class VerifyApiView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    @swagger_auto_schema(
        request_body=CodeSerializer,
        responses={
            201: openapi.Response(
                description='User created successfully',
                examples={
                    'application/json': {
                        "status": True,
                        "auth_status": 'EMAIL',
                        "access_token": 'sfgdsrgdsgdth234858hdcd4d5x6w4856cw4o8n5w4',
                        "refresh_token": 'srcnhow45740756cwtyw804e8nt89w5to8750ty8tcy8ern',
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

    def post(self, request, *args, **kwargs):
        user = self.request.user
        code = self.request.data.get('code')

        self.check_verify(user, code)
        data = {
            "status": True,
            "auth_status": user.auth_status,
            "access_token": user.token()['access'],
            "refresh_token": user.token()['refresh_token'],
        }
        return Response(data)

    @staticmethod
    def check_verify(user, code):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), code=code, is_confirmed=False)
        if not verifies.exists():
            data = {
                "message": "Tasdiqlash kodingiz xato yoki eskirgan"
            }
            raise ValidationError(data)
        verifies.update(is_confirmed=True)
        if user.auth_status not in DONE:
            user.auth_status = CODE_VERIFIED
            user.save()

        return True


class GetNewVerificationCodeView(APIView):
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        user = request.user
        self.check_verification(user)
        code = user.create_verify_code()
        send_email(user.email, code)

        return Response(
            {
                "success": True,
                "message": "Tasdiqlash kodi qaytadan jo'natildi"
            }
        )

    @staticmethod
    def check_verification(user):
        verifies = user.verify_codes.filter(expiration_time__gte=datetime.now(), is_confirmed=False)
        if verifies.exists():
            data = {
                "success": False,
                "message": "Sizga kod yuborilgan iltimos biroz kuting... "
            }
            raise ValidationError(data)


class ChangeUserInformationView(UpdateAPIView):
    permission_classes = (permissions.IsAuthenticated, )
    serializer_class = ChangeUserInformation
    http_method_names = ['patch', 'put']

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        super(ChangeUserInformationView, self).update(request, *args, **kwargs)
        data = {
            "success": True,
            'message': "User updated successfully",
            'auth_status': self.request.user.auth_status
        }

        return Response(data, status=200)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
