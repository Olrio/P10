from rest_framework.permissions import BasePermission
from projects.models import Contributors, Projects, Issues
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.exceptions import NotFound



class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsProjectAuthor(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not the author of this project"

    def has_object_permission(self, request, view, obj):
        return obj.author_user_id == request.user


class IsProjectContributor(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not a contributor to this project"

    def has_object_permission(self, request, view, obj):
        return Contributors.objects.filter(project=obj).filter(user=request.user).exists()


class CanReadContributors(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not a contributor to this project"

    def has_object_permission(self, request, view, obj):
        return obj.filter(user=request.user).exists()


class CanModifyContributors(BasePermission):
    message = "Sorry, you don't have permission to access the collaborators informations." \
              "You're not the author of this project"

    def has_object_permission(self, request, view, obj):
        return request.user == Projects.objects.get(id=request.parser_context['kwargs']['project_pk']).author_user_id


class CanReadIssues(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not a contributor to this project"

    def has_object_permission(self, request, view, obj):
        return Contributors.objects.filter(
            project=Projects.objects.get(id=request.parser_context['kwargs']['project_pk']),
            user=request.user).exists()


class CanModifyIssues(BasePermission):
    message = "Sorry, you don't have permission to update or delete this issue." \
              "You're not the author of this issue"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author_user_id


class IsIssueInThisProject(BasePermission):
    message = "This issue isn't related to this project"

    def has_object_permission(self, request, view, obj):
        try:
            Projects.objects.get(id=request.parser_context['kwargs']['project_pk'])
        except ObjectDoesNotExist:
            raise NotFound(detail=f"Sorry, project {request.parser_context['kwargs']['project_pk']} doesn't exist")
        return obj.project_id.id == int(request.parser_context['kwargs']['project_pk'])


class CanReadComments(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not a contributor to this project"

    def has_object_permission(self, request, view, obj):
        return Contributors.objects.filter(
            project=Projects.objects.get(id=request.parser_context['kwargs']['project_pk']),
            user=request.user).exists()


class CanModifyComment(BasePermission):
    message = "Sorry, you don't have permission to update or delete this comment." \
              "You're not the author of this comment"

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author_user_id


class IsIssueCommentsInThisProject(BasePermission):
    message = "This issue isn't related to this project"

    def has_object_permission(self, request, view, obj):
        return Issues.objects.get(id=int(request.parser_context['kwargs']['issue_pk'])).project_id == \
               Projects.objects.get(id=int(request.parser_context['kwargs']['project_pk']))


class IsCommentInThisIssue(BasePermission):
    message = "This comment insn't related to this issue"

    def has_object_permission(self, request, view, obj):
        return obj.issue_id.id == int(request.parser_context['kwargs']['issue_pk'])
