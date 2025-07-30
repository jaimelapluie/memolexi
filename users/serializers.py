from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "password", "email", "first_name", "telegram_id", "main_language"]
        extra_kwargs = {
            "password": {"write_only": True}  # Пароль только для записи
        }
        
    def create(self, validated_data):
        # Извлекаю пароль из данных
        password = validated_data.pop("password", None)
        # Создаю пользователя без пароля
        user = self.Meta.model(**validated_data)
        # Устанавливаю пароль с хэшированием
        if password is not None:
            user.set_password(password)
        user.save()
        return user
        
        
class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = get_user_model()
        fields = ("username", "email", "password", "password2")
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают!"})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")  # Удаляем повтор пароля
        user = get_user_model().objects.create_user(**validated_data)
        return user


class DeleteAccountSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True)
    
    
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password2 = serializers.CharField(required=True)
    
    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError({"confirm_password": "Пароли не совпадают"})
        return data
    
    def validate_new_password(self, value):
        if len(value) < 3:
            raise serializers.ValidationError('Пароль коротковат')
        return value
    
    
class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    
    
class SetNewPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password2 = serializers.CharField(write_only=True, min_length=8)
    
    def validate(self, data):
        if data['new_password'] == data['new_password2']:
            return data
        raise serializers.ValidationError("Oops.. passwords do not match")
    