"""softdesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, \
    TokenObtainPairView
from rest_framework_nested import routers

from projects.views import (
    ProjectsViewset,
    IssuesViewset,
    ContributorsViewset,
    CommentsViewset,
)
from authentication.views import UserViewset, RegisterUserViewset

router = routers.SimpleRouter()
router.register("projects", ProjectsViewset, basename="projects")

issues_router = routers.NestedSimpleRouter(
    router, "projects", lookup="project")
issues_router.register("issues", IssuesViewset, basename="issues")

contributors_router = routers.NestedSimpleRouter(
    router, "projects", lookup="project")
contributors_router.register(
    "users", ContributorsViewset, basename="contributors")

comments_router = routers.NestedSimpleRouter(
    issues_router, "issues", lookup="issue")
comments_router.register("comments", CommentsViewset, basename="comments")

router.register("user", UserViewset, basename="user")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/refresh/", TokenRefreshView.as_view(),
         name="token_refresh"),
    path("api/", include(router.urls)),
    path("api/", include(issues_router.urls)),
    path("api/", include(contributors_router.urls)),
    path("api/", include(comments_router.urls)),
    path("api/signup/", RegisterUserViewset.as_view(), name="signup"),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
]
