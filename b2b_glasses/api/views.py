import logging  # <--- 1. ДОБАВЛЕН ИМПОРТ
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

from users.models import User, TelegramLinkToken
from .serializers import (
    BotRegistrationSerializer, SetPasswordSerializer,
    UpdatePhoneSerializer, UserLoginSerializer
)
from .permissions import IsBot

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

logger = logging.getLogger(__name__)  # <--- 2. ПОЛУЧАЕМ ЛОГГЕР


class BotRegistrationView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(...)
    def post(self, request, *args, **kwargs):
        serializer = BotRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            reg_data = serializer.validated_data

            try:
                token = TelegramLinkToken.objects.select_related(
                    'user').get(token=reg_data['token'])
            except TelegramLinkToken.DoesNotExist:
                # 3. ЛОГИРУЕМ ОШИБКУ
                logger.warning(
                    f"Неудачная регистрация: Токен не найден или уже использован ({reg_data['token']})")
                return Response(
                    {"error": "Токен не найден или уже был использован"},
                    status=status.HTTP_404_NOT_FOUND
                )

            user = token.user
            user.telegram_id = reg_data['telegram_id']
            # ... (остальные поля) ...
            user.phone_number = reg_data['phone_number']
            user.telegram_username = reg_data.get('username')
            user.telegram_first_name = reg_data.get('first_name') or ''
            user.telegram_last_name = reg_data.get('last_name') or ''
            if not user.first_name:
                user.first_name = reg_data.get('first_name') or ''
            if not user.last_name:
                user.last_name = reg_data.get('last_name') or ''

            user.set_password(reg_data['password'])
            user.is_active = True
            user.save()
            token.delete()

            # 4. ЛОГИРУЕМ УСПЕХ
            logger.info(
                f"Успешная регистрация: Пользователь {user.username} (TG ID: {user.telegram_id}) привязан.")
            return Response(
                {"message": "Аккаунт успешно создан и привязан"},
                status=status.HTTP_200_OK
            )

        # 5. ЛОГИРУЕМ ОШИБКУ ВАЛИДАЦИИ
        logger.warning(
            f"Неудачная регистрация (Ошибка 400): {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(...)
    def post(self, request, *args, **kwargs):
        serializer = SetPasswordSerializer(
            instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Пользователь {request.user.username} успешно сменил пароль.")
            return Response(
                {"message": "Пароль успешно установлен"},
                status=status.HTTP_200_OK
            )
        logger.warning(
            f"Неудачная смена пароля (Ошибка 400): {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckUserStatusView(APIView):
    permission_classes = [IsBot]

    @swagger_auto_schema(auto_schema=None)
    def get(self, request, *args, **kwargs):
        telegram_id = request.query_params.get('telegram_id')
        if not telegram_id:
            logger.warning("CheckUserStatusView: Запрос без telegram_id")
            return Response({"error": "telegram_id не указан"}, status=status.HTTP_400_BAD_REQUEST)

        user_exists = User.objects.filter(
            telegram_id=telegram_id,
            is_active=True
        ).exists()

        logger.debug(
            f"CheckUserStatusView: Проверка статуса {telegram_id}. Результат: {user_exists}")
        if user_exists:
            return Response({"status": "active"}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "inactive"}, status=status.HTTP_404_NOT_FOUND)


User = get_user_model()


class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(...)
    def post(self, request, *args, **kwargs):
        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Неудачный вход (Ошибка 400): {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        login = serializer.validated_data['login']
        password = serializer.validated_data['password']

        user = User.objects.filter(
            Q(telegram_username=login) |
            Q(phone_number=login) |
            Q(username=login)
        ).first()

        if user and user.check_password(password) and user.is_active:
            token, created = Token.objects.get_or_create(user=user)
            logger.info(
                f"Успешный вход: Пользователь {user.username} вошел через браузер.")
            company_name = user.company.name if getattr(user, 'company', None) else None
            return Response({
                'token': token.key,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'company': company_name,
                    'phone_number': user.phone_number or '',
                    'telegram_username': user.telegram_username or '',
                    'email': user.email or '',
                }
            }, status=status.HTTP_200_OK)

        logger.warning(
            f"Неудачный вход (Ошибка 401): Неверные учетные данные для логина '{login}'.")
        return Response(
            {"error": "Неверные учетные данные"},
            status=status.HTTP_401_UNAUTHORIZED
        )


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Auth (Авторизация)'],
        operation_summary="Получить профиль текущего пользователя",
        responses={200: "Данные профиля", 401: "Не авторизован"}
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        company_name = user.company.name if getattr(user, 'company', None) else None
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "company": company_name,
            "phone_number": user.phone_number or "",
            "telegram_username": user.telegram_username or "",
            "email": user.email or "",
        }, status=status.HTTP_200_OK)

