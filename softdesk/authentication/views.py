from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from django.contrib.auth.models import User
from authentication.serializers import UserSerializer, RegisterUserSerializer


class UserViewset(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()


class RegisterUserViewset(generics.CreateAPIView):
    serializer_class = RegisterUserSerializer
