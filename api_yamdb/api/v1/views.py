
from django.contrib.auth.tokens import default_token_generator
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.generics import get_object_or_404
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
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
from users.models import User

from api_yamdb.api.v1.serializers import UserCreateSerializer


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
