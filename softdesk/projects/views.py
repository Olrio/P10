from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from projects.models import Projects, Issues, Contributors, Comments
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework.exceptions import NotFound
from projects.serializers import ProjectsListSerializer, \
    ProjectsDetailSerializer, IssuesListSerializer, IssuesDetailSerializer, \
    ContributorsListSerializer, ContributorsDetailSerializer, CommentsListSerializer, \
    CommentsDetailSerializer
from projects.permissions import IsAuthenticated, IsProjectAuthor, IsProjectContributor,\
    CanReadContributors, CanModifyContributors, CanReadIssues, CanModifyIssues, \
    IsIssueInThisProject, CanReadComments, IsCommentInThisIssue, CanModifyComment, \
    IsIssueCommentsInThisProject



class MultipleSerializerMixin:
    detail_serializer_class = None

    def get_serializer_class(self):
        if self.action == 'retrieve' and self.get_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ProjectsListSerializer
    detail_serializer_class = ProjectsDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)
        Contributors.objects.create(
            user=self.request.user,
            project=Projects.objects.get(id=serializer.data['id']),
            role='AUTHOR'
        )

    def get_queryset(self):
        if not self.request.parser_context['kwargs']:
            self.permission_classes = [IsAuthenticated]
            return Projects.objects.filter(contributors__user=self.request.user)
        elif self.request.parser_context['kwargs']['pk']:
            self.permission_classes = [IsAuthenticated, IsProjectAuthor]
            queryset = Projects.objects.filter(id=self.request.parser_context['kwargs']['pk'])
            return queryset


class IssuesViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer

    def get_queryset(self):
        if 'pk' not in self.request.parser_context['kwargs']:
            self.permission_classes = [IsAuthenticated, CanReadIssues]
            try:
                self.check_object_permissions(self.request,
                                              obj=Issues.objects.filter(project_id__id=self.request.parser_context['kwargs']['project_pk']))
                queryset = Issues.objects.filter(project_id__id=self.request.parser_context['kwargs']['project_pk'])
                return queryset
            except ObjectDoesNotExist:
                raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
        else:
            self.permission_classes = [IsAuthenticated, IsIssueInThisProject, CanModifyIssues]
            queryset = Issues.objects.filter(id=self.request.parser_context['kwargs']['pk'])
            return queryset

    def perform_create(self, serializer):
        self.permission_classes = [IsAuthenticated, IsProjectContributor]
        try:
            self.check_object_permissions(self.request, Projects.objects.get(
                id=self.request.parser_context['kwargs']['project_pk']))
            serializer.save(author_user_id=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']).author_user_id,
                            project_id=Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk']))
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")


class ContributorsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorsListSerializer
    detail_serializer_class = ContributorsDetailSerializer

    def get_queryset(self):
        try:
            Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk'])
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
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

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            raise serializers.ValidationError({"contributor deletion error: "
                                               "you can't remove yourself as a contributor "
                                               "of this project since you are the author"},)
        else:
            instance.delete()


class CommentsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CommentsListSerializer
    detail_serializer_class = CommentsDetailSerializer

    def get_queryset(self):
        if 'pk' not in self.request.parser_context['kwargs']:
            self.permission_classes = [IsAuthenticated, IsIssueCommentsInThisProject, CanReadComments]
            try:
                Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk'])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
            try:
                Issues.objects.get(id=self.request.parser_context['kwargs']['issue_pk'])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, issue {self.request.parser_context['kwargs']['issue_pk']} doesn't exist")
            self.check_object_permissions(self.request,
                                          obj=Comments.objects.filter(
                                              issue_id__project_id__id=self.request.parser_context['kwargs']['project_pk']))
            queryset = Comments.objects.filter(issue_id__project_id__id=self.request.parser_context['kwargs']['project_pk'])
            return queryset

        else:
            try:
                Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk'])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
            try:
                Issues.objects.get(id=self.request.parser_context['kwargs']['issue_pk'])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, issue {self.request.parser_context['kwargs']['issue_pk']} doesn't exist")
            try:
                Comments.objects.get(id=self.request.parser_context['kwargs']['pk'])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, comment {self.request.parser_context['kwargs']['pk']} doesn't exist")

            if self.request.method == 'GET':
                self.permission_classes = [IsAuthenticated, IsIssueCommentsInThisProject, CanReadComments,
                                           IsCommentInThisIssue,
                                           ]
            else:
                self.permission_classes = [IsAuthenticated, IsIssueCommentsInThisProject, CanReadComments,
                                           CanModifyComment,
                                           IsCommentInThisIssue,
                                           ]
            self.check_object_permissions(self.request,
                                          obj=Comments.objects.get(id=self.request.parser_context['kwargs'][
                                                  'pk']))
            queryset = Comments.objects.filter(id=self.request.parser_context['kwargs']['pk'])
            return queryset

    def perform_create(self, serializer):
        self.permission_classes = [IsAuthenticated, IsIssueCommentsInThisProject, CanReadComments]
        try:
            Projects.objects.get(id=self.request.parser_context['kwargs']['project_pk'])
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {self.request.parser_context['kwargs']['project_pk']} doesn't exist")
        try:
            Issues.objects.get(id=self.request.parser_context['kwargs']['issue_pk'])
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, issue {self.request.parser_context['kwargs']['issue_pk']} doesn't exist")
        self.check_object_permissions(self.request,
                                      obj=Comments.objects.filter(
                                          issue_id__project_id__id=self.request.parser_context['kwargs']['project_pk']))
        serializer.save(issue_id=Issues.objects.get(id=self.request.parser_context['kwargs']['issue_pk']),
                        author_user_id=self.request.user)
