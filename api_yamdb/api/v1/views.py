from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, UpdateModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView


from users.models import User
from .serializers import (
    UserSerializer,
    JWTSerializer
)


class UserViewSet(
    GenericViewSet,
    ListModelMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny,]

    class Meta:
        model = User


class JWTView(TokenObtainPairView):
    serializer_class = JWTSerializer


class UserSignUpView(APIView):
    pass
