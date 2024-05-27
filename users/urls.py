from django.urls import path
from .views import CreateUserView, VerifyApiView, GetNewVerificationCodeView, ChangeUserInformationView, LoginView

urlpatterns = [
    path('login/', LoginView.as_view()),
    path('signup/', CreateUserView.as_view()),
    path('verify/', VerifyApiView.as_view()),
    path('new-verify/', GetNewVerificationCodeView.as_view()),
    path('change-information/', ChangeUserInformationView.as_view()),
]
