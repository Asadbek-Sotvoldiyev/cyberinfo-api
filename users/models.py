import uuid
from datetime import datetime, timedelta
from django.utils import timezone
import random
from django.core.validators import FileExtensionValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework_simplejwt.tokens import RefreshToken
from shared.models import BaseModel


ORDINARY, MANAGER, ADMIN = ('ordinary', 'manager', 'admin')
NEW, CODE_VERIFIED, DONE = ('new', 'code_verified', 'done')


class User(BaseModel, AbstractUser):
    USER_ROLES = (
        (ORDINARY, ORDINARY),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN)
    )
    AUTH_STATUSES = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE)
    )
    user_role = models.CharField(max_length=15, choices=USER_ROLES, default=ORDINARY)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUSES, default=NEW)
    phone_number = models.CharField(max_length=13, unique=True, null=True, blank=True)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True,
                              validators=[
                                  FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'heic', 'heif'])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self):
        code = "".join([str(random.randint(0, 10000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id=self.id,
            code=code
        )
        return code

    def check_username(self):
        if not self.username:
            temp_username = f'cyberinfo-{uuid.uuid4().__str__().split("-")[-1]}'
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.randint(0,9)}"
            self.username = temp_username

    def check_email(self):
        if self.email:
            normalize_email = self.email.lower()  # aKhamdjon@gmail.com -> akhamdjon@gmail.com
            self.email = normalize_email

    def check_pass(self):
        if not self.password:
            temp_password = f'password-{uuid.uuid4().__str__().split("-")[-1]}' #  123456mfdsjfkd
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith('pbkdf2_sha256'):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh)
        }

    def save(self, *args, **kwargs):
        self.clean()
        super(User, self).save(*args, **kwargs)

    def clean(self):
        self.check_email()
        self.check_username()
        self.check_pass()
        self.hashing_password()


class UserConfirmation(BaseModel):
    code =models.CharField(max_length=4)
    user = models.ForeignKey('users.User', models.CASCADE, related_name='verify_codes')
    expiration_time = models.DateTimeField(null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        self.expiration_time = timezone.now() + timedelta(minutes=2)
        super(UserConfirmation, self).save(*args, **kwargs)

