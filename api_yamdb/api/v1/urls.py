from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)
from .views import JWTView, UserViewSet

router_v1 = DefaultRouter()

router_v1.register(
    'users',
    UserViewSet,
    basename='users'
)



auth_urls = [
    path(
        'signup/',
        ...,
        name='signup'
    ),
    path(
        'token/',
        JWTView.as_view(),
        name='token_obtain_pair'
    )
]

urlpatterns = [
    path('auth/', include(auth_urls)),
]