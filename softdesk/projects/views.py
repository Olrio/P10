from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from projects.models import Projects, Issues
from django.contrib.auth.models import User
from projects.serializers import ProjectsListSerializer, \
    ProjectsDetailSerializer, IssuesListSerializer, IssuesDetailSerializer
from projects.permissions import IsAuthenticated


class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.get_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ProjectsListSerializer
    detail_serializer_class = ProjectsDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Projects.objects.filter(author=self.request.user)


class IssuesViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Issues.objects.all()

    def get_serializer_class(self):
        return super().get_serializer_class()
