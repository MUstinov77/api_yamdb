from django.urls import include, path
from rest_framework.routers import DefaultRouter
from api.v1 import views

reviews_url = r'titles/(?P<title_id>\d+)/reviews'
comments_url = rf'{reviews_url}/(?P<review_id>\d+)/comments'

router_v1 = DefaultRouter()
router_v1.register(
    'genres',
    views.GenreViewSet,
    basename='genres'
)
router_v1.register(
    'categories',
    views.CategoriesViewSet,
    basename='categories'
)
router_v1.register(
    'titles',
    views.TitleViewSet,
    basename='titles'
)
# Нужен пагинатор
router_v1.register(
    reviews_url,
    views.ReviewViewSet,
    basename='reviews'
)
# Нужен пагинатор
router_v1.register(
    comments_url,
    views.CommentViewSet,
    basename='comments'
)
router_v1.register(
    'users',
    views.UserViewSet,
    basename='users'
)

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
    path('', include(router_v1.urls))
]
