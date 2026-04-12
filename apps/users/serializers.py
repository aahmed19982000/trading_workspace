from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import CustomUser, UserProfile


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = "email"


class RegisterSerializer(serializers.ModelSerializer):
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
                {"password_confirm": "كلمتا المرور غير متطابقتين."}
            )
        return attrs

    def create(self, validated_data):
        profile_data = {
            "trading_goal": validated_data.pop("trading_goal", ""),
            "experience_level": validated_data.pop("experience_level", "beginner"),
            "preferred_market": validated_data.pop("preferred_market", "mixed"),
            "risk_appetite": validated_data.pop("risk_appetite", ""),
        }
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")

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
