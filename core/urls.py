from django.urls import path
from rest_framework_simplejwt.views import (
    TokenBlacklistView,
    TokenRefreshView,
    TokenVerifyView,
)
from apps.users.views import (
    CurrentUserView,
    EmailTokenObtainPairView,
    LoginPageView,
    RegisterView,
    RegisterPageView,
    UserProfileView,
    WorkspaceDetailView,
    WorkspaceHomeView,
    WorkspaceListCreateView,
)

urlpatterns = [
    path("", LoginPageView.as_view(), name="login_page"),
    path("login/", LoginPageView.as_view(), name="login_page_alias"),
    path("api/register/", RegisterView.as_view(), name="register"),
    path("api/me/", CurrentUserView.as_view(), name="current_user"),
    path("api/profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/workspaces/", WorkspaceListCreateView.as_view(), name="workspace_list"),
    path(
        "api/workspaces/<int:pk>/",
        WorkspaceDetailView.as_view(),
        name="workspace_detail",
    ),
    path("api/token/", EmailTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("register/", RegisterPageView.as_view(), name="register_page"),
    path("workspace/", WorkspaceHomeView.as_view(), name="workspace_home"),
]
