from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают!"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")  # Удаляем повтор пароля
        # user = User.objects.create_user(**validated_data)
        # return user


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    