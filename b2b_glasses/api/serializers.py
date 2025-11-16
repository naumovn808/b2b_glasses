from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class BotRegistrationSerializer(serializers.Serializer):
    """
    Сериализатор для НОВОЙ регистрации через бота.
    """
    token = serializers.UUIDField()
    telegram_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)

    # --- ИЗМЕНЕНИЕ: Убрана проверка min_length=8 ---
    password = serializers.CharField(write_only=True, required=True)

    # Необязательные поля
    username = serializers.CharField(
        max_length=150, required=False, allow_null=True, allow_blank=True)
    first_name = serializers.CharField(
        max_length=150, required=False, allow_null=True, allow_blank=True)
    last_name = serializers.CharField(
        max_length=150, required=False, allow_null=True, allow_blank=True)

    # --- ИЗМЕНЕНИЕ: Функция validate_password УДАЛЕНА ---
    # (Так как мы отключили валидаторы в settings.py)


class SetPasswordSerializer(serializers.ModelSerializer):
    """
    Сериализатор для УСТАНОВКИ/СМЕНЫ пароля (для тех, кто уже вошел).
    """
    password = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('password', 'password_confirm')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Пароли не совпадают."})

        # --- ИЗМЕНЕНИЕ: Убрана валидация ---
        # (т.к. мы отключили ее в settings.py)
        # try:
        #     validate_password(attrs['password'], self.instance)
        # except ValidationError as e:
        #     raise serializers.ValidationError({"password": list(e.messages)})

        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UpdatePhoneSerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()
    phone_number = serializers.CharField(max_length=20)


class UserLoginSerializer(serializers.Serializer):
    login = serializers.CharField(
        required=True,
        help_text="Имя пользователя, Telegram Username или Номер телефона"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
