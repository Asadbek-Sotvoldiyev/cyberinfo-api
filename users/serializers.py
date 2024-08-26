from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User, CODE_VERIFIED, DONE, NEW
from shared.utils import send_email, check_user_type, username


class SignUpSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)

    def __init__(self, *args, **kwargs):
        super(SignUpSerializer, self).__init__(*args, **kwargs)
        self.fields['email'] = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'id',
            'auth_status'
        )
        extra_kwargs = {
            'auth_status': {'read_only': True, 'required': False},
        }

    def create(self, validated_data):
        email = validated_data.pop('email', None)
        user = super(SignUpSerializer, self).create(validated_data)

        if email:
            user.email = email
            code = user.create_verify_code()
            send_email(user.email, code)
        user.save()

        return user

    def validate(self, data):
        super(SignUpSerializer, self).validate(data)
        self.auth_validate(data)
        return data

    @staticmethod
    def auth_validate(data):
        user_input = str(data.get('email')).lower()
        if not user_input:
            data = {
                'success': False,
                'message': "You must send email"
            }
            raise ValidationError(data)
        return data

    def validate_email(self, value):
        if value and User.objects.filter(email=value).exists():
            res = {
                "status": False,
                "Message": "Email already exists"
            }
            raise ValidationError(res)
        return value

    def to_representation(self, instance):
        data = super(SignUpSerializer, self).to_representation(instance)
        data.update(instance.token())

        return data


class ChangeUserInformation(serializers.Serializer):
    first_name = serializers.CharField(write_only=True, required=True)
    last_name = serializers.CharField(write_only=True, required=True)
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    def validate(self, data):
        password = data.get('password', None)
        confirm_password = data.get('confirm_password', None)

        if confirm_password != password:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Passwords don't match"
                }
            )
        if password:
            validate_password(password)
            validate_password(confirm_password)

        return data

    def validate_username(self, username):
        if len(username) < 5 or len(username) > 30:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Username must be between 5 and 30 characters"
                }
            )
        if username.isdigit():
            raise ValidationError(
                {
                    "success": False,
                    "message": "This username is entirely numeric"
                }
            )

        return username

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.password = validated_data.get('password', instance.password)

        if validated_data.get('password'):
            instance.set_password(validated_data.get('password'))
        if instance.auth_status == CODE_VERIFIED:
            instance.auth_status = DONE
        instance.save()
        return instance


class LoginSerializer(TokenObtainPairSerializer):

    def __init__(self,*args, **kwargs):
        super(LoginSerializer, self).__init__(*args, **kwargs)
        self.fields['userinput'] = serializers.CharField(required=True)
        self.fields['username'] = serializers.CharField(required=False, read_only=True)
        self.fields['phone_number'] = serializers.CharField(required=False, read_only=True)

    def auth_validate(self, data):
        user_input = data.get('userinput')
        if check_user_type(user_input) == 'username':
            username = user_input
        elif check_user_type(user_input) == 'email':
            user = self.get_user(email__iexact=user_input)
            username = user.username
        elif check_user_type(user_input) == 'phone':
            user = User.objects.filter(phone_number=user_input).first()
            username = user.username
        else:
            data = {
                "success": True,
                "message": "Siz email, telefon raqam yoki username jo'natishingiz kerak"
            }
            raise ValidationError(data)

        authentications_kwargs = {
            self.username_field: username,
            'password': data['password']
        }

        current_user = User.objects.filter(username__iexact=username).first()
        if current_user.auth_status in [NEW, CODE_VERIFIED]:
            raise ValidationError(
                {
                    "success": False,
                    "message": "Siz ro'yxatdan to'liq o'tmagansiz"
                }
            )
        user = authenticate(**authentications_kwargs)
        if user is not None:
            self.user = user
        else:
            raise ValidationError({
                "success": False,
                "message": "Sorry! Login or password you entered is incorrect. Please check and try again."
            })

    def validate(self, data):
        self.auth_validate(data)
        if self.user.auth_status not in [DONE, ]:
            raise PermissionDenied("Siz login qila olmaysiz. Ruxsastingiz yo'q")
        data = self.user.token()
        data['auth_status'] = self.user.auth_status
        return data

    def get_user(self, **kwargs):
        users = User.objects.filter(**kwargs)
        if not users.exists():
            raise ValidationError({
                "message": "No active account found"
            })
        return users.first()


class CodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=4)
