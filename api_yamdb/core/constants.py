# Константы для модели пользователя
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_EMAIL = 254

# Константы для остальных моделей
LENG_MAX = 256
LENG_CUT = 30
MIN_SCORE = 1
MAX_SCORE = 10

# Роли пользователей
USER_ROLES = {
    'user': 'user',
    'admin': 'admin',
    'moderator': 'moderator'
}

# Тема письма при отправки токена
CONFIRM_CODE_MESSAGE = 'Код для подтверждения регистрации на api_yamdb'


ADDITIONAL_USER_FIElDS = (
    (None, {
        'fields': (
            'bio',
            'role',
        )
    }),
)

FORBIDDEN_SIMBOLS_REGEX = r'^[\w.@+-]+$'

FORBIDDEN_NAMES = (
    'me',
)

RATING_DEFAULT_VALUE = 1
