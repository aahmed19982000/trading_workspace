from django.conf import settings
from django.utils import translation
from django.views.generic import TemplateView
from rest_framework import generics, permissions
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import EmailTokenObtainPairSerializer, RegisterSerializer


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
