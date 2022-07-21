from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from projects.models import Projects, Issues, Contributors
from django.contrib.auth.models import User
from projects.serializers import ProjectsListSerializer, \
    ProjectsDetailSerializer, IssuesListSerializer, IssuesDetailSerializer, \
    ContributorsListSerializer, ContributorsDetailSerializer
from projects.permissions import IsAuthenticated, IsProjectAuthor, IsProjectContributor



class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.get_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ProjectsListSerializer
    detail_serializer_class = ProjectsDetailSerializer
    permission_classes = [IsAuthenticated, IsProjectContributor]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        Contributors.objects.create(
            user=self.request.user,
            project=Projects.objects.get(id=serializer.data['id']),
            role='AUTHOR'
        )

    def get_queryset(self):
        # IsProjectAuthor is only related to detail view, i.e. url contains kwargs corresponding to project.id
        if self.request.parser_context['kwargs']['pk']:
            self.check_object_permissions(self.request, obj=Contributors.objects.filter(
                project__id=self.request.parser_context['kwargs']['pk']))
            return Projects.objects.filter(id=self.request.parser_context['kwargs']['pk'])
        return Projects.objects.filter(author=self.request.user.id)


class IssuesViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        self.check_object_permissions(self.request,
                                      obj=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
        current_project_id = self.request.parser_context['kwargs']['project_pk']
        queryset = Issues.objects.filter(project__id=current_project_id)
        return queryset

    def get_serializer_class(self):
        return super().get_serializer_class()


class ContributorsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorsListSerializer
    detail_serializer_class = ContributorsDetailSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        self.check_object_permissions(self.request,
                                      obj=Projects.objects.filter(id=self.request.parser_context['kwargs']['project_pk']))
        current_project_id = self.request.parser_context['kwargs']['project_pk']
        queryset = Contributors.objects.filter(project__id=current_project_id, project__author=self.request.user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(project=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
