from rest_framework.viewsets import ModelViewSet
from rest_framework import serializers
from projects.models import Projects, Issues, Contributors, Comments
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound
from projects.serializers import (
    ProjectsListSerializer,
    ProjectsDetailSerializer,
    IssuesListSerializer,
    IssuesDetailSerializer,
    ContributorsListSerializer,
    ContributorsDetailSerializer,
    CommentsListSerializer,
    CommentsDetailSerializer,
)
from projects.permissions import (
    IsAuthenticated,
    IsProjectAuthor,
    IsProjectContributor,
    IsProjectContributorViaComment,
    IsIssueAuthor,
    IsCommentAuthor,
)


class MultipleSerializerMixin:
    detail_serializer_class = None
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "retrieve" and self.get_serializer_class is not None:
            return self.detail_serializer_class
        return super().get_serializer_class()


class ProjectsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ProjectsListSerializer
    detail_serializer_class = ProjectsDetailSerializer

    def perform_create(self, serializer):
        serializer.save(author_user_id=self.request.user)
        Contributors.objects.create(
            user=self.request.user,
            project=Projects.objects.get(id=serializer.data["id"]),
            role="AUTHOR",
        )

    def get_queryset(self):
        if not self.request.parser_context["kwargs"]:
            return Projects.objects.filter(
                contributors__user=self.request.user)
        elif self.request.parser_context["kwargs"]["pk"]:
            project_pk = self.request.parser_context["kwargs"]["pk"]
            try:
                Projects.objects.get(id=project_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, project {project_pk} doesn't exist"
                )
            self.permission_classes = [IsProjectAuthor]
            queryset = Projects.objects.filter(
                id=self.request.parser_context["kwargs"]["pk"]
            )
            return queryset


class IssuesViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = IssuesListSerializer
    detail_serializer_class = IssuesDetailSerializer

    def get_queryset(self):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        try:
            Projects.objects.get(id=project_pk)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {project_pk} doesn't exist"
            )
        # list serializer needs IsProjectContributor permission
        if "pk" not in self.request.parser_context["kwargs"]:
            self.permission_classes = [IsProjectContributor]
            self.check_object_permissions(
                self.request,
                obj=Projects.objects.get(id=project_pk)
            )
            queryset = Issues.objects.filter(
                project_id__id=project_pk
            )
            return queryset
        # detail serializer needs IsIssueAuthor permission
        else:
            issue_pk = self.request.parser_context['kwargs']['pk']
            try:
                Issues.objects.get(
                    id=issue_pk)
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, issue "
                           f"{issue_pk}"
                           f" doesn't exist"
                )
            if not Projects.objects.filter(id=project_pk,
                                           issues=int(issue_pk)).exists():
                raise serializers.ValidationError(
                    {
                        "Issue error":
                            "This issue isn't related to this project"}
                )
            self.permission_classes = [
                IsIssueAuthor,
            ]
            self.check_object_permissions(
                self.request,
                obj=Issues.objects.get(
                    id=issue_pk),
            )
            queryset = Issues.objects.filter(
                id=issue_pk
            )
            return queryset

    def perform_create(self, serializer):
        # POST method uses list serializer
        # so needs IsProjectContributor permission
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        self.permission_classes = [IsProjectContributor]
        try:
            self.check_object_permissions(
                self.request,
                Projects.objects.get(id=project_pk),
            )
            serializer.save(
                author_user_id=Projects.objects.get(
                    id=project_pk).author_user_id,
                project_id=Projects.objects.get(id=project_pk),
            )
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {project_pk} doesn't exist"
            )


class ContributorsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = ContributorsListSerializer
    detail_serializer_class = ContributorsDetailSerializer

    def get_queryset(self):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        try:
            Projects.objects.get(id=project_pk)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {project_pk} doesn't exist"
            )
        if "pk" not in self.request.parser_context["kwargs"].keys():
            self.permission_classes = [IsProjectContributor]
            self.check_object_permissions(
                self.request,
                obj=Projects.objects.get(id=project_pk)
            )
            return Contributors.objects.filter(project__id=project_pk)
        elif "pk" in self.request.parser_context["kwargs"].keys():
            try:
                Contributors.objects.get(
                    id=self.request.parser_context["kwargs"]["pk"])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, contributor "
                           f"{self.request.parser_context['kwargs']['pk']}"
                           f" doesn't exist"
                )
            if not Contributors.objects.filter(
                id=self.request.parser_context["kwargs"]["pk"],
                project__id=project_pk,
            ).exists():
                raise serializers.ValidationError(
                    {
                        "contributor selection error: "
                        "This is not a contributor of this project"
                    },
                )
            self.permission_classes = [IsProjectAuthor]
            self.check_object_permissions(self.request,
                                          obj=Projects.objects.get(
                                              id=project_pk))
            queryset = Contributors.objects.filter(
                id=self.request.parser_context["kwargs"]["pk"],
                project=self.request.parser_context["kwargs"]["project_pk"],
            )
            return queryset

    def perform_create(self, serializer):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        self.permission_classes = [IsProjectAuthor]
        try:
            self.check_object_permissions(
                self.request,
                Projects.objects.get(id=project_pk),
            )
            serializer.save(
                project=Projects.objects.get(id=project_pk)
            )
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {project_pk} doesn't exist"
            )

    def perform_destroy(self, instance):
        if instance.user == self.request.user:
            raise serializers.ValidationError(
                {
                    "contributor deletion error: "
                    "you can't remove yourself as a contributor "
                    "of this project since you are the author"
                },
            )
        else:
            instance.delete()


class CommentsViewset(MultipleSerializerMixin, ModelViewSet):
    serializer_class = CommentsListSerializer
    detail_serializer_class = CommentsDetailSerializer

    def existing_objects(self):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        issue_pk = self.request.parser_context['kwargs']['issue_pk']
        try:
            Projects.objects.get(id=project_pk)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, project {project_pk} doesn't exist"
            )
        try:
            Issues.objects.get(id=issue_pk)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f"Sorry, issue {issue_pk} doesn't exist"
            )

        if not Projects.objects.filter(id=project_pk,
                                       issues=int(issue_pk)).exists():
            raise serializers.ValidationError(
                {
                    "Issue error": "This issue isn't related to this project"}
            )
        if "pk" in self.request.parser_context["kwargs"]:
            try:
                Comments.objects.get(
                    id=self.request.parser_context["kwargs"]["pk"])
            except ObjectDoesNotExist:
                raise NotFound(
                    detail=f"Sorry, comment "
                           f"{self.request.parser_context['kwargs']['pk']} "
                           f"doesn't exist"
                )

    def get_queryset(self):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        issue_pk = self.request.parser_context['kwargs']['issue_pk']
        self.existing_objects()
        if "pk" not in self.request.parser_context["kwargs"]:
            self.permission_classes = [IsProjectContributor]
            self.check_object_permissions(
                self.request,
                obj=Projects.objects.get(id=project_pk)
            )
            queryset = Comments.objects.filter(issue_id=issue_pk)
            return queryset

        elif "pk" in self.request.parser_context['kwargs'] and \
                self.request.method == "GET":
            self.permission_classes = [IsProjectContributorViaComment]
            return Comments.objects.filter(
                id=self.request.parser_context["kwargs"]["pk"])

        else:
            self.permission_classes = [
                IsProjectContributorViaComment,
                IsCommentAuthor,
            ]
            queryset = Comments.objects.filter(
                id=self.request.parser_context["kwargs"]["pk"]
            )
            return queryset

    def perform_create(self, serializer):
        project_pk = self.request.parser_context["kwargs"]["project_pk"]
        self.existing_objects()
        self.permission_classes = [IsProjectContributor]
        self.check_object_permissions(
            self.request,
            obj=Projects.objects.get(id=project_pk)
        )
        serializer.save(
            issue_id=Issues.objects.get(
                id=self.request.parser_context["kwargs"]["issue_pk"]
            ),
            author_user_id=self.request.user,
        )
