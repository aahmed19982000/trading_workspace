from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from apps.users.views import EmailTokenObtainPairView

urlpatterns = [
    path("api/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
