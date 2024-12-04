from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView
)

v1_router = DefaultRouter()

auth_urls = [
    path(
        'signup/',
        ...,
        name='signup'
    ),
    path(
        'token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    )
]

urlpatterns = [
    path('auth/', include(auth_urls)),
]