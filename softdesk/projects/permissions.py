from rest_framework.permissions import BasePermission
from projects.models import Contributors


# Authentication
class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


# Authorization
class IsProjectContributor(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "this project and its related informations."
        "You're not a contributor to this project"
    )

    def has_object_permission(self, request, view, obj):
        return (
            Contributors.objects.filter(
                project=obj).filter(user=request.user).exists()
        )


class IsProjectContributorViaComment(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "this project and its related informations."
        "You're not a contributor to this project"
    )

    def has_object_permission(self, request, view, obj):
        return (
            Contributors.objects.filter(
                project=obj.issue_id.project_id).
            filter(user=request.user).exists()
        )


# Access
class IsProjectAuthor(BasePermission):
    message = (
        "Sorry, you don't have permission to access "
        "this project and its related informations."
        "You're not the author of this project"
    )

    def has_object_permission(self, request, view, obj):
        return obj.author_user_id == request.user


class IsIssueAuthor(BasePermission):
    message = (
        "Sorry, you don't have permission to update or delete this issue."
        "You're not the author of this issue"
    )

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author_user_id


class IsCommentAuthor(BasePermission):
    message = (
        "Sorry, you don't have permission to update or delete this comment."
        "You're not the author of this comment"
    )

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author_user_id


class IsContributorsLeader(BasePermission):
    message = (
        "Sorry, you don't have permission to delete a contributor."
        "You're not the author of this project"
    )

    def has_object_permission(self, request, view, obj):
        return request.user == obj.project.author_user_id
