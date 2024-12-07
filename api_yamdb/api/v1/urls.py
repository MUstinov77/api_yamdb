from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.v1 import views

router_v1 = DefaultRouter()

router_v1.register(
    'users',
    views.UserViewSet,
    basename='users'
)

auth_urls = [
    path(
        'signup/',
        views.UserCreateViewSet.as_view({'post': 'create'}),
        name='signup'
    ),
    path(
        'token/',
        views.JWTView.as_view(),
        name='token'
    )
]

urlpatterns = [
    path('auth/', include(auth_urls)),
]
