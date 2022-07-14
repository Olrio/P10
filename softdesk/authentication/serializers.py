from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class RegisterUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(
            queryset=User.objects.all(),
            message='This email address is already registered. Please use another one'
        )]
    )
    username = serializers.CharField(
        min_length=3,
        validators=[UniqueValidator(queryset=User.objects.all(),
                                    message='This username already exists. Please choose another one',
                                    )]
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        if data['email'] != data['email'].lower():
            raise serializers.ValidationError(
                {'Email case error': 'Only lowercase characters are allowed in mail address'})
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "your two entries differ !"})
        return data

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user



