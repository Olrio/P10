from rest_framework.viewsets import ReadOnlyModelViewSet

from projects.models import Projects
from projects.serializers import ProjectsSerializer

class ProjectsViewset(ReadOnlyModelViewSet):
    serializer_class = ProjectsSerializer

    def get_queryset(self):
        return Projects.objects.all()
