from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsProjectAuthor(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not the author of this project"

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsProjectContributor(BasePermission):
    message = "Sorry, you don't have permission to access this project and its related informations." \
              "You're not a contributor to this project"

    def has_object_permission(self, request, view, obj):
        for item in obj:
            if request.user == item.user:
                return True
        return False
