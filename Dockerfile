# استخدام إصدار Python مستقر وخفيف
FROM python:3.12-slim

# منع Python من كتابة ملفات .pyc وتعطيل الـ buffering لظهور اللوجات فوراً
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# تثبيت اعتماديات النظام الضرورية (لقاعدة البيانات وأدوات الـ SEO)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    gettext \
    && apt-get clean

# إعداد مجلد العمل
WORKDIR /app

# تثبيت مكتبات Python
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# نسخ ملفات المشروع
COPY . /app/
