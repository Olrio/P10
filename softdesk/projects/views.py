from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from projects.models import Projects, Issues
from projects.serializers import ProjectsSerializer, IssuesSerializer


class ProjectsViewset(ReadOnlyModelViewSet):
    serializer_class = ProjectsSerializer

    def get_queryset(self):
        return Projects.objects.all()


class IssuesViewset(ModelViewSet):
    serializer_class = IssuesSerializer

    def get_queryset(self):
        return Issues.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()
