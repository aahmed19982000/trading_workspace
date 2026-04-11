from .base import *

# 1. إيقاف وضع التطوير فوراً
DEBUG = False

# 2. تحديد النطاقات المسموح لها بتشغيل الموقع (أضف دومين موقعك هنا)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['yourdomain.com'])

# 3. إعدادات قاعدة البيانات للإنتاج
# سيتم سحب البيانات من متغير DATABASE_URL في السيرفر
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# 4. إعدادات الأمان الصارمة (Security)
# تجعل الموقع لا يعمل إلا عبر https
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# حماية من الهجمات الشائعة
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# 5. إعدادات الملفات الساكنة (Static Files)
# في الإنتاج يفضل استخدام WhiteNoise أو خادم منفصل
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 6. إعدادات البريد الإلكتروني الحقيقية (SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')

# 7. إدارة سجلات الأخطاء (Logging)
# لكي يتم حفظ الأخطاء في ملفات بدلاً من عرضها للمستخدم
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'production_errors.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}