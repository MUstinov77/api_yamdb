from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.v1 import views

router_v1 = DefaultRouter()

auth_urls = [
    path(
        'signup/',
        views.SignUpView.as_view(),
        name='signup'
    ),
    path(
        'token/',
        views.GetTokenView.as_view(),
        name='token'
    )
]

urlpatterns = [
    path('auth/', include(auth_urls)),
]
