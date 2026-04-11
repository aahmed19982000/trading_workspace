from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """مدير المستخدمين للتعامل مع البريد الإلكتروني بدل اسم المستخدم."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("يجب توفير بريد إلكتروني صالح")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """مستخدم مخصص للمنصة يعتمد على البريد الإلكتروني بدل اسم المستخدم."""

    TRADER_LEVELS = (
        ("beginner", "مبتدئ"),
        ("pro", "محترف"),
        ("expert", "خبير"),
    )

    username = None
    email = models.EmailField("البريد الإلكتروني", unique=True)
    phone_number = models.CharField("رقم الهاتف", max_length=15, blank=True, null=True)
    bio = models.TextField("نبذة تعريفية", blank=True, null=True)
    avatar = models.ImageField(
        "الصورة الشخصية", upload_to="avatars/", null=True, blank=True
    )
    trader_level = models.CharField(
        max_length=20, choices=TRADER_LEVELS, default="beginner"
    )
    timezone = models.CharField("المنطقة الزمنية", max_length=64, default="UTC")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "مستخدم"
        verbose_name_plural = "المستخدمين"


class UserProfile(models.Model):
    """ملف شخصي تفصيلي للمستخدم منفصل عن بيانات المصادقة الأساسية."""

    EXPERIENCE_LEVELS = (
        ("beginner", "مبتدئ"),
        ("intermediate", "متوسط"),
        ("advanced", "متقدم"),
        ("professional", "محترف"),
    )
    PREFERRED_MARKETS = (
        ("forex", "فوركس"),
        ("stocks", "أسهم"),
        ("crypto", "عملات رقمية"),
        ("commodities", "سلع"),
        ("indices", "مؤشرات"),
        ("mixed", "متنوع"),
    )

    user = models.OneToOneField(
        "users.CustomUser",
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="المستخدم",
    )
    trading_goal = models.CharField("الهدف التداولي", max_length=255, blank=True)
    experience_level = models.CharField(
        "مستوى الخبرة",
        max_length=20,
        choices=EXPERIENCE_LEVELS,
        default="beginner",
    )
    preferred_market = models.CharField(
        "السوق المفضل",
        max_length=20,
        choices=PREFERRED_MARKETS,
        default="mixed",
    )
    risk_appetite = models.CharField("شهية المخاطرة", max_length=20, blank=True)
    onboarding_completed = models.BooleanField("اكتمل الإعداد الأولي", default=False)
    created_at = models.DateTimeField("تاريخ الإنشاء", auto_now_add=True)
    updated_at = models.DateTimeField("تاريخ التحديث", auto_now=True)

    def __str__(self):
        return f"Profile for {self.user.email}"

    class Meta:
        verbose_name = "ملف المستخدم"
        verbose_name_plural = "ملفات المستخدمين"
