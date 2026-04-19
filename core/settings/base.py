import os
import sys
from pathlib import Path
import environ
from datetime import timedelta
from django.utils.translation import gettext_lazy as _

# 1. مسارات المشروع
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, os.path.join(BASE_DIR, "apps"))

# 2. المتغيرات البيئية
env = environ.Env(DEBUG=(bool, True))
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# 3. الإعدادات الأساسية
SECRET_KEY = env("SECRET_KEY", default="django-insecure-your-key-here")
DEBUG = True
ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1", "web"]

# 4. التطبيقات
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
]

LOCAL_APPS = [
    "apps.users.apps.UsersConfig",
    "apps.strategies.apps.StrategiesConfig",
    "apps.trading.apps.TradingConfig",
    "apps.ai_analysis.apps.AiAnalysisConfig",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# 5. Middleware
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# 6. القوالب
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# 7. قاعدة البيانات
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "trading_db",
        "USER": "django_user",
        "PASSWORD": "django_pass",
        "HOST": "db",
        "PORT": "5432",
    }
}

# 8. Redis والكاش
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL", default="redis://redis:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# 9. Celery
CELERY_BROKER_URL = env("REDIS_URL", default="redis://redis:6379/1")
CELERY_RESULT_BACKEND = env("REDIS_URL", default="redis://redis:6379/1")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

# 10. المستخدم المخصص
AUTH_USER_MODEL = "users.CustomUser"

# 11. قوة كلمة المرور
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        )
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# 12. REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "EXCEPTION_HANDLER": "core.exceptions.custom_exception_handler",
}

# 13. CORS
DEFAULT_CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

CORS_ALLOWED_ORIGINS = env.list(
    "CORS_ALLOWED_ORIGINS",
    default=DEFAULT_CORS_ALLOWED_ORIGINS,
)
CORS_ALLOW_CREDENTIALS = True

# 14. اللغة والتوقيت
LANGUAGE_CODE = "ar"
LANGUAGES = [
    ("en", _("English")),
    ("ar", _("Arabic")),
]
LOCALE_PATHS = [os.path.join(BASE_DIR, "locale")]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# 15. الملفات الساكنة والمرفوعات
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# 16. الأمان
FERNET_KEY = env("FERNET_KEY", default="")
GEMINI_API_KEY = env("GEMINI_API_KEY", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 17. JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}
