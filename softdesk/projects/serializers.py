from rest_framework import serializers

from projects.models import Projects, Issues


class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'author', 'issues']


class IssuesSerializer(serializers.ModelSerializer):

    class Meta:
        model = Issues
        fields = ['id', 'title', 'project', 'assignee', 'author']
