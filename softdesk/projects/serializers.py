from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db  import IntegrityError

from projects.models import Projects, Issues, Contributors
from django.contrib.auth.models import User
from authentication.serializers import UserSerializer


class ContributorsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributors
        fields = ['id', 'user', 'role']

    def create(self, validated_data):
        try:
            return super().create(validated_data)

        except IntegrityError as error:
            raise ValidationError(
                {"unique constaint failed": 'This user is already a contributor to this project'}) from error


class ContributorsDetailSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Contributors
        fields = ['id', 'user', 'role']

    def get_user(self, instance):
        queryset = User.objects.filter(id=instance.user.id)
        serializer = UserSerializer(queryset, many=True)
        return serializer.data


class IssuesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issues
        fields = ['id', 'title', 'project', 'assignee', 'author']


class IssuesDetailSerializer(serializers.ModelSerializer):
    project = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()

    class Meta:
        model = Issues
        fields = ['id', 'title', 'project', 'assignee', 'author']

    def get_project(self, instance):
        queryset = Projects.objects.filter(id=instance.project.id)
        serializer = ProjectsListSerializer(queryset, many=True)
        return serializer.data


class ProjectsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'description', 'type']


class ProjectsDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = ['id', 'title', 'issues', 'description', 'type']

    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializer = IssuesListSerializer(queryset, many=True)
        return serializer.data



