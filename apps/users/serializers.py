from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, UserProfile, Workspace


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"

    def validate(self, attrs):
        email = (attrs.get("email") or "").strip()
        password = attrs.get("password")

        if not email or not password:
            raise AuthenticationFailed(
                _("Please enter your email and password."),
                code="authentication_failed",
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if user is None:
            raise AuthenticationFailed(
                _("Invalid credentials. Please verify your email and password."),
                code="authentication_failed",
            )

        if not user.is_active:
            raise AuthenticationFailed(
                _("This account is inactive."),
                code="authentication_failed",
            )

        refresh = self.get_token(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class RegisterSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    trading_goal = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    experience_level = serializers.ChoiceField(
        choices=UserProfile.EXPERIENCE_LEVELS,
        write_only=True,
        required=False,
        default="beginner",
    )
    preferred_market = serializers.ChoiceField(
        choices=UserProfile.PREFERRED_MARKETS,
        write_only=True,
        required=False,
        default="mixed",
    )
    risk_appetite = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "password",
            "password_confirm",
            "phone_number",
            "bio",
            "trader_level",
            "timezone",
            "is_email_verified",
            "trading_goal",
            "experience_level",
            "preferred_market",
            "risk_appetite",
        ]
        read_only_fields = ["id", "is_email_verified"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": _("Passwords do not match.")}
            )
        return attrs

    def create(self, validated_data):
        full_name = validated_data.pop("full_name", "").strip()
        profile_data = {
            "trading_goal": validated_data.pop("trading_goal", ""),
            "experience_level": validated_data.pop("experience_level", "beginner"),
            "preferred_market": validated_data.pop("preferred_market", "mixed"),
            "risk_appetite": validated_data.pop("risk_appetite", ""),
        }
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

        if full_name:
            name_parts = full_name.split(None, 1)
            validated_data["first_name"] = name_parts[0]
            if len(name_parts) > 1:
                validated_data["last_name"] = name_parts[1]

        user = CustomUser.objects.create_user(password=password, **validated_data)
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def to_representation(self, instance):
        profile = getattr(instance, "profile", None)
        return {
            "id": instance.id,
            "email": instance.email,
            "phone_number": instance.phone_number,
            "bio": instance.bio,
            "trader_level": instance.trader_level,
            "timezone": instance.timezone,
            "is_email_verified": instance.is_email_verified,
            "profile": {
                "trading_goal": profile.trading_goal if profile else "",
                "experience_level": profile.experience_level if profile else "beginner",
                "preferred_market": profile.preferred_market if profile else "mixed",
                "risk_appetite": profile.risk_appetite if profile else "",
                "onboarding_completed": (
                    profile.onboarding_completed if profile else False
                ),
            },
        }


class CurrentUserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "phone_number",
            "bio",
            "trader_level",
            "timezone",
            "is_email_verified",
            "profile",
        ]

    def get_full_name(self, obj):
        full_name = f"{obj.first_name} {obj.last_name}".strip()
        return full_name or obj.email

    def get_profile(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile:
            return {
                "trading_goal": "",
                "experience_level": "beginner",
                "preferred_market": "mixed",
                "risk_appetite": "",
                "onboarding_completed": False,
            }

        return {
            "trading_goal": profile.trading_goal,
            "experience_level": profile.experience_level,
            "preferred_market": profile.preferred_market,
            "risk_appetite": profile.risk_appetite,
            "onboarding_completed": profile.onboarding_completed,
        }


class WorkspaceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = Workspace
        fields = [
            "id",
            "user_id",
            "name",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user_id", "created_at", "updated_at"]

    def validate_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError(_("Workspace name is required."))
        return value

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    trader_level = serializers.ChoiceField(
        choices=CustomUser.TRADER_LEVELS,
        required=False,
    )
    timezone = serializers.CharField(required=False, allow_blank=True)
    trading_goal = serializers.CharField(required=False, allow_blank=True)
    experience_level = serializers.ChoiceField(
        choices=UserProfile.EXPERIENCE_LEVELS,
        required=False,
    )
    preferred_market = serializers.ChoiceField(
        choices=UserProfile.PREFERRED_MARKETS,
        required=False,
    )
    risk_appetite = serializers.CharField(required=False, allow_blank=True)
    onboarding_completed = serializers.BooleanField(required=False)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "full_name",
            "first_name",
            "last_name",
            "phone_number",
            "bio",
            "trader_level",
            "timezone",
            "is_email_verified",
            "trading_goal",
            "experience_level",
            "preferred_market",
            "risk_appetite",
            "onboarding_completed",
        ]
        read_only_fields = ["id", "is_email_verified"]

    def to_representation(self, instance):
        profile = getattr(instance, "profile", None)
        full_name = f"{instance.first_name} {instance.last_name}".strip()
        return {
            "id": instance.id,
            "email": instance.email,
            "full_name": full_name or instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "phone_number": instance.phone_number,
            "bio": instance.bio,
            "trader_level": instance.trader_level,
            "timezone": instance.timezone,
            "is_email_verified": instance.is_email_verified,
            "trading_goal": profile.trading_goal if profile else "",
            "experience_level": profile.experience_level if profile else "beginner",
            "preferred_market": profile.preferred_market if profile else "mixed",
            "risk_appetite": profile.risk_appetite if profile else "",
            "onboarding_completed": (
                profile.onboarding_completed if profile else False
            ),
        }

    def update(self, instance, validated_data):
        profile, _created = UserProfile.objects.get_or_create(user=instance)

        full_name = validated_data.pop("full_name", None)
        profile_fields = [
            "trading_goal",
            "experience_level",
            "preferred_market",
            "risk_appetite",
            "onboarding_completed",
        ]
        profile_data = {
            field: validated_data.pop(field)
            for field in profile_fields
            if field in validated_data
        }

        if full_name is not None:
            name_parts = full_name.strip().split(None, 1)
            instance.first_name = name_parts[0] if name_parts else ""
            instance.last_name = name_parts[1] if len(name_parts) > 1 else ""

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        profile.save()

        return instance
