from rest_framework.serializers import ModelSerializer

from users.models import User



USER_ROLES = (
    ('user', 'user'),
    ('moderator', 'moderator'),
    ('admin', 'admin'),
)