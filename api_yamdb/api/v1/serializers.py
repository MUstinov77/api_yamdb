from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )


class UserCreateSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        return User.objects.create(
            username=validated_data.get('username'),
            email=validated_data.get('email')
        )

    class Meta:
        model = User
        fields = (
            'username',
            'email'
        )




class JWTSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['username'] = self.user.username
        data['email'] = self.user.email
        return data
