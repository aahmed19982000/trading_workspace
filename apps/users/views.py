from django.conf import settings
from django.utils import translation
from django.views.generic import TemplateView
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CurrentUserSerializer,
    EmailTokenObtainPairSerializer,
    RegisterSerializer,
    UserProfileSerializer,
    WorkspaceSerializer,
)


class LoginPageView(TemplateView):
    template_name = "auth/login.html"

    def dispatch(self, request, *args, **kwargs):
        lang = request.GET.get("lang")
        supported_languages = {code for code, _name in settings.LANGUAGES}

        if lang and lang in supported_languages:
            translation.activate(lang)
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang

        return super().dispatch(request, *args, **kwargs)


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]


class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = CurrentUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class WorkspaceListCreateView(generics.ListCreateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.workspaces.all()

    def put(self, request, *args, **kwargs):
        workspace_id = request.data.get("id")
        if not workspace_id:
            raise ValidationError({"id": "Workspace id is required."})

        instance = generics.get_object_or_404(self.get_queryset(), pk=workspace_id)
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class WorkspaceDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = WorkspaceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.request.user.workspaces.all()


class RegisterPageView(TemplateView):
    template_name = "auth/register.html"

    def dispatch(self, request, *args, **kwargs):
        lang = request.GET.get("lang")
        supported_languages = {code for code, _name in settings.LANGUAGES}
        if lang and lang in supported_languages:
            translation.activate(lang)
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang
        return super().dispatch(request, *args, **kwargs)


class WorkspaceHomeView(TemplateView):
    template_name = "workspace/home.html"
