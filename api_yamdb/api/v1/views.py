from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (
    permissions,
    status,
    views,
    viewsets,
)
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken

from api.v1 import serializers
from api.v1.filters import TitleFilter
from api.v1.view_sets import CreateListDestroyViewSet
from api.v1.permissions import (
    IsAdminUserOrReadOnly,
    IsAuthorModeratorAdminSuperUserOrReadOnly,
    IsSuperUserOrIsAdminOnly
)
from api.v1.serializers import (
    CategorySerializer,
    GenreSerializer,
    JWTSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserCreateSerializer,
    UserSerializer
)
from reviews.models import (
    Category,
    Genre,
    Review,
    Title
)
from users.models import User


class UserCreateView(views.APIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class UserViewSet(
    viewsets.ModelViewSet
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [SearchFilter, ]
    search_fields = ('username',)
    permission_classes = (
        permissions.IsAuthenticated,
        IsSuperUserOrIsAdminOnly
    )
    lookup_field = 'username'
    http_method_names = [
        'get',
        'post',
        'patch',
        'delete',
    ]

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='me',
        url_name='me',
    )
    def get_me(self, request):
        """Получение пользователем подробной информации о себе."""
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


class JWTView(views.APIView):
    """Вьюсет для получения пользователем JWT токена."""

    queryset = User.objects.all()
    serializer_class = JWTSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        """Предоставляет пользователю JWT токен по коду подтверждения."""
        serializer = JWTSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        message = {'token': str(AccessToken.for_user(user))}
        return Response(message, status=status.HTTP_200_OK)


class GenreViewSet(CreateListDestroyViewSet):
    """Получить список всех жанров.Права доступа:Доступно без токена."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesViewSet(CreateListDestroyViewSet):
    """Получить список всех категорий.Права доступа:Доступно без токена."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(ModelViewSet):
    """Управление произведениями."""

    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    ).all().order_by('-year')
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    http_method_names = (
        'get',
        'post',
        'delete',
        'patch'
    )

    def get_serializer_class(self):
        if self.action in permissions.SAFE_METHODS:
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(ModelViewSet):
    """
    Управление отзывами.
    """

    serializer_class = serializers.ReviewSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminSuperUserOrReadOnly
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_title(self):
        return get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=self.get_title()
        )


class CommentViewSet(ModelViewSet):
    """Управление комментариями."""

    serializer_class = serializers.CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorModeratorAdminSuperUserOrReadOnly
    )
    http_method_names = (
        'get',
        'post',
        'patch',
        'delete',
    )

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all().select_related('author')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
