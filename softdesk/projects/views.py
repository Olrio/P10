from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.decorators import action
from projects.models import Projects, Issues, Contributors
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from projects.serializers import ProjectsListSerializer, \
    ProjectsDetailSerializer, IssuesListSerializer, IssuesDetailSerializer, \
    ContributorsListSerializer, ContributorsDetailSerializer
from projects.permissions import IsAuthenticated, IsProjectAuthor, IsProjectContributor, CanReadContributors, CanModifyContributors



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
        serializer.save(author_user_id=self.request.user)
        Contributors.objects.create(
            user=self.request.user,
            project=Projects.objects.get(id=serializer.data['id']),
            role='AUTHOR'
        )

    def get_queryset(self):
        if not self.request.parser_context['kwargs']:
            return Projects.objects.filter(contributors__user=self.request.user)
        elif self.request.parser_context['kwargs']['pk']:
            queryset = Projects.objects.filter(id=self.request.parser_context['kwargs']['pk'])
            return queryset


class IssuesViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer
    permission_classes = [IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        try:
            self.check_object_permissions(self.request,
                                          obj=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
            current_project_id = self.request.parser_context['kwargs']['project_pk']
            queryset = Issues.objects.filter(project__id=current_project_id)
            return queryset
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")

    def get_serializer_class(self):
        return super().get_serializer_class()

    def perform_create(self, serializer):
        self.permission_classes = [IsAuthenticated, IsProjectContributor]
        try:
            self.check_object_permissions(self.request, Projects.objects.get(
                id=self.request.parser_context['kwargs']['project_pk']))
            serializer.save(author=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']).author_user_id,
                            project=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")


class ContributorsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorsListSerializer
    detail_serializer_class = ContributorsDetailSerializer

    def get_queryset(self):
        if 'pk' not in self.request.parser_context['kwargs'].keys():
            self.permission_classes = [IsAuthenticated, CanReadContributors]
            self.check_object_permissions(self.request, Contributors.objects.filter(
                project__id=self.request.parser_context['kwargs']['project_pk']))
            return Contributors.objects.filter(project__id=self.request.parser_context['kwargs']['project_pk'])
        elif 'pk' in self.request.parser_context['kwargs'].keys():
            self.permission_classes = [IsAuthenticated, CanModifyContributors]
            queryset = Contributors.objects.filter(
                id=self.request.parser_context['kwargs']['pk'],
                project=self.request.parser_context['kwargs']['project_pk']
            )
            return queryset

    def perform_create(self, serializer):
        self.permission_classes = [IsAuthenticated, IsProjectAuthor]
        try:
            self.check_object_permissions(self.request, Projects.objects.get(
                id=self.request.parser_context['kwargs']['project_pk']))
            serializer.save(project=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
