from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from database.models import Projects
from django.contrib.auth.models import User
from database.serializers import ProjectsSerializer, UserSerializer

class ProjectsViewset(ReadOnlyModelViewSet):
    serializer_class = ProjectsSerializer

    def get_queryset(self):
        return Projects.objects.all()


class UserViewset(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all()