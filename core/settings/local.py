from .base import *

# 1. تفعيل وضع التطوير
# WARNING: لا تترك هذا True في السيرفر الحقيقي أبداً
DEBUG = True

# 2. السماح لجميع الأجهزة بالاتصال محلياً
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# 3. إعدادات قاعدة البيانات (PostgreSQL)
# تأكد أن بيانات الاتصال تطابق ما وضعته في ملف docker-compose.yml
DATABASES = {
    'default': env.db('DATABASE_URL', default='postgres://postgres:password@localhost:5432/trading_db')
}

# 4. إعدادات البريد الإلكتروني للتطوير
# سيقوم بطباعة رسائل تفعيل الحساب في "الترمينال" بدلاً من إرسال إيميل حقيقي
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 5. إعدادات التحقق من قوة كلمة المرور
# يمكن إضعافها في مرحلة التطوير لتسهيل إنشاء حسابات تجريبية
AUTH_PASSWORD_VALIDATORS = []

# 6. إعدادات CORS للتطوير (للربط مع React)
CORS_ALLOW_ALL_ORIGINS = True 

# 7. إعدادات الملفات الساكنة محلياً
STATIC_URL = '/static/'