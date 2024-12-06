from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db import transaction
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import mixins, viewsets

from api.v1.permissions import (
    IsSuperUserOrAdmin,
)
from api.v1.serializers import (
    SignUpSerializer,
    GetTokenSerializer,
    UserSerializer
)
from core.constants import subject
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
    Comment
)
from api.v1.serializers import (
    CategorySerializer,
    GenreSerializer,
    TitleSerializer,
    ReviewSerializer,
    CommentSerializer,
    UserSerializer
)
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
                    status=status.HTTP_200_OK
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


class UserViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter,]
    search_fields = ('username',)
    permission_classes = (
        IsAuthenticated,
        IsSuperUserOrAdmin
    )

    def get_user(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
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


class GenreViewSet(ModelViewSet):
    """
    Управление жанрами.

    Позволяет просматривать, создавать и удалять жанры для администрации,
    а для обычных пользователей доступен только GET-запрос.
    """

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(ModelViewSet):
    """
    Управление категориями.

    Позволяет просматривать, создавать и удалять категории для администрации,
    а для обычных пользователей доступен только GET-запрос.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(ModelViewSet):
    """
    Управление произведениями.
    """

    # Поля genre и category отправляются не словарём.
    # Нет поля rating
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class ReviewViewSet(ModelViewSet):
    """
    Управление отзывами.
    """

    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title__id=title_id)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CommentViewSet(ModelViewSet):
    """
    Управление комментариями.
    """

    serializer_class = CommentSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')
        return Comment.objects.filter(
            review__id=review_id, review__title__id=title_id
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class UserViewSet(ModelViewSet):
    """
    Управление пользователями.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
