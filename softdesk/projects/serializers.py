from rest_framework import serializers

from projects.models import Projects, Issues


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
        fields = ['id', 'title']


class ProjectsDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = ['id', 'title', 'issues']

    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializer = IssuesListSerializer(queryset, many=True)
        return serializer.data



