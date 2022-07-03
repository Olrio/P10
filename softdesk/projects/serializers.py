from rest_framework.serializers import ModelSerializer

from projects.models import Projects

class ProjectsSerializer(ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'author']

