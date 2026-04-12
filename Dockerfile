# استخدام نسخة بايثون خفيفة ومتوافقة مع Apple Silicon
FROM python:3.11-slim

# إعداد متغيرات البيئة لمنع بايثون من كتابة ملفات .pyc وتحديث المخرجات فوراً
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# تثبيت التبعيات الضرورية للنظام (لربط PostgreSQL)
RUN apt-get update && apt-get install -y \
    build-essential \
    gettext \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات وتثبيته
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# نسخ بقية ملفات المشروع
COPY . /app/
