from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from apps.users.views import (
    EmailTokenObtainPairView,
    LoginPageView,
    RegisterView,
    RegisterPageView,
)

urlpatterns = [
    path("", LoginPageView.as_view(), name="login_page"),
    path("login/", LoginPageView.as_view(), name="login_page_alias"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("register/", RegisterPageView.as_view(), name="register_page"),
]
