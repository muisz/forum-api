from rest_framework import serializers

from .models import User


class RegisterUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = User
        fields = ("name", "username", "password")

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class AuthUserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.name
    
    def get_token(self, obj):
        if hasattr(obj, "token"):
            return obj.token
        return None

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "username",
            "last_login",
            "token",
        )
