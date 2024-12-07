
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import mixins, viewsets

from api.v1.permissions import (
    IsSuperUserOrAdmin,
)
from api.v1.serializers import (
    UserCreateSerializer,
    JWTSerializer,
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
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
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
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
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
        url_path='r(?P<username>[\w.@+-]+)',
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


class JWTView(TokenObtainPairView):
    serializer_class = JWTSerializer


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

    queryset = Title.objects.all().annotate(
        # Добавляет в поле rating ср. арифм. всех отзывов
        rating=Avg('reviews__score')
    ).order_by('id')
    serializer_class = TitleSerializer


class ReviewViewSet(ModelViewSet):
    """
    Управление отзывами.
    """

    serializer_class = ReviewSerializer

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title__id=title_id).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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
        ).order_by('id')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


