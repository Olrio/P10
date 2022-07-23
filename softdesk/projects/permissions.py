from rest_framework.permissions import BasePermission
from projects.models import Contributors, Projects


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
