from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
)
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken

from users.models import CommonUser



class UserCreateView(
    GenericViewSet,
    CreateModelMixin
):
    queryset = CommonUser.objects.all()
    serializer_class = ...
    permission_classes = [AllowAny,]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer
