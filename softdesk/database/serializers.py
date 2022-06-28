from rest_framework.serializers import ModelSerializer

from database.models import Projects
from django.contrib.auth.models import User

class ProjectsSerializer(ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'author']

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']