
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.filters import TitleFilter
from api.v1.permissions import (
    IsSuperUserOrAdmin,
    IsAuthorModeratorAdminSuperUserOrReadOnly,
    IsAdminUserOrReadOnly
)
from api.v1.serializers import (
    UserCreateSerializer,
    JWTSerializer,
    UserSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    CategorySerializer,
    GenreSerializer
)
from reviews.models import (
    Category,
    Genre,
    Title,
    Review,
)
from api.v1 import serializers
from core.utils import send_confirmation_code
from users.models import User


class UserCreateViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin
):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        user = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).first()
        if user:
            confirmation_code = default_token_generator.make_token(user)
            send_confirmation_code(
                email=user.email,
                code=confirmation_code
            )
            return Response(
                status=status.HTTP_200_OK
            )
        else:
            serializer = UserCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = User.objects.create(**serializer.validated_data)
            confirmation_code = default_token_generator.make_token(user)
            send_confirmation_code(
                email=user.email,
                code=confirmation_code
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
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
        permissions.IsAuthenticated,
        IsSuperUserOrAdmin
    )

    @action(
        detail=False,
        methods=['get', 'patch', 'delete'],
        url_path=r'(?P<username>[\w.@+-]+)',
        url_name='get_user',
    )
    def get_user(self, request, username):
        user = get_object_or_404(User, username=username)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        elif request.method == 'DELETE':
            user.delete()
            return Response(
                status=status.HTTP_204_NO_CONTENT
            )
        serializer = UserSerializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me',
        url_name='me',
    )
    def get_me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(
                role=request.user.role
            )
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )
        serializer = UserSerializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class JWTView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    """Вьюсет для получения пользователем JWT токена."""

    queryset = User.objects.all()
    serializer_class = JWTSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        """Предоставляет пользователю JWT токен по коду подтверждения."""
        serializer = JWTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get('confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(user, confirmation_code):
            message = {'confirmation_code': 'Код подтверждения невалиден'}
            return Response(message, status=status.HTTP_400_BAD_REQUEST)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class GenreViewSet(ModelViewSet):
    """Получить список всех жанров.Права доступа:Доступно без токена."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class CategoriesViewSet(ModelViewSet):
    """Получить список всех категорий.Права доступа:Доступно без токена."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSet):
    """Управление произведениями."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all()
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter
    http_method_names = [
        'get',
        'post',
        'delete',
        'patch'
    ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    """
    Управление отзывами.
    """

    serializer_class = serializers.ReviewSerializer
    permission_classes = (IsAuthorModeratorAdminSuperUserOrReadOnly,)

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to create a review.")
        serializer.save(author=self.request.user, title=self.get_title())

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод "PUT" не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)


class CommentViewSet(ModelViewSet):
    """
    Управление комментариями.
    """

    serializer_class = serializers.CommentSerializer
    permission_classes = (IsAuthorModeratorAdminSuperUserOrReadOnly,)

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all().select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def update(self, request, *args, **kwargs):
        if request.method == 'PUT':
            return Response(
                {'detail': 'Метод "PUT" не разрешен.'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED
            )
        return super().update(request, *args, **kwargs)
