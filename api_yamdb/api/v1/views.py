from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.serializers import (
    SignUpSerializer,
    GetTokenSerializer
)
from core.constants import subject
from users.models import User


class SignUpView(APIView):
    """
    Обработка POST-запроса на создание пользователя.

    Зарегистрировать нового пользователя и отправить на его email
    сообщение с кодом подтверждения.
    """

    def post(self, request):
        """Обработка POST-запроса."""
        serializer = SignUpSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                user = serializer.save()
                confirmation_code = default_token_generator.make_token(user)

                try:
                    self.send_code(user.email, confirmation_code)
                except Exception as e:
                    # В случае ошибки при отправке email откатим создание
                    user.delete()
                    return Response(
                        {
                            "error": str(e)
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                return Response(
                    serializer.data,
                    status=status.HTTP_201_CREATED
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def send_code(email, confirmation_code):
        """Отправка кода на email после её проверки."""
        # Может отправить в спам
        send_mail(
            subject=subject,
            message=f"Код для подтверждения регистрации: {confirmation_code}",
            from_email=None,
            recipient_list=[email]
        )


class GetTokenView(APIView):
    """
    Обработка POST-запроса на получение JWT токена.

    Получить код подтверждения и имя пользователя, а после дать JWT токен.
    """

    def post(self, request):
        """Создание JWT токен."""
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            username, confirmation_code = serializer.validated_data.values()
            user = get_object_or_404(User, username=username)
            if not default_token_generator.check_token(
                user,
                confirmation_code
            ):
                return Response(
                    {
                        "confirmation_code":
                        "Код подтверждения неверный"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            token_str = str(AccessToken.for_user(user))
            return Response(
                {
                    "token": str(token_str),
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
