
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import mixins, viewsets
from rest_framework_simplejwt.tokens import AccessToken

from api.v1.permissions import (
    IsSuperUserOrAdmin,
)
from api.v1.serializers import (
    UserCreateSerializer,
    JWTSerializer,
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
        serializer.save()
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
