from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.db  import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from projects.models import Projects, Issues, Contributors, Comments
from authentication.models import User
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
        fields = ['id', 'title', 'desc', 'assignee_user_id', 'author_user_id', 'tag', 'priority', 'status', 'created_time']
        read_only_fields = ['author_user_id']

    def validate(self, data):
        try:
            Projects.objects.get(id=self.context['request'].parser_context['kwargs']['project_pk'])
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                    {"Project error": f"project {self.context['request'].parser_context['kwargs']['project_pk']} doesn't exist"})
        if 'assignee_user_id' in data.keys():
            if not Contributors.objects.filter(user=data['assignee_user_id'], project=Projects.objects.get(id=self.context['request'].parser_context['kwargs']['project_pk'])).exists():
                raise serializers.ValidationError(
                    {'Assignee case error': 'assignee must be a contributor in this project'})
        else:
            data['assignee_user_id'] = self.context['request'].user
        return data


class IssuesDetailSerializer(serializers.ModelSerializer):
    author_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Issues
        fields = ['id', 'title', 'desc', 'assignee_user_id', 'author_user_id', 'project_id']
        read_only_fields = ['author_user_id', 'project_id']

    def get_author_user_id(self, instance):
        queryset = User.objects.filter(id=instance.author_user_id.id)
        serializer = UserSerializer(queryset, many=True)
        return serializer.data


class ProjectsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ['id', 'title', 'description', 'type', 'author_user_id']
        read_only_fields = ['author_user_id']


class ProjectsDetailSerializer(serializers.ModelSerializer):
    issues = serializers.SerializerMethodField()

    class Meta:
        model = Projects
        fields = ['id', 'title', 'issues', 'description', 'type']

    def get_issues(self, instance):
        queryset = instance.issues.all()
        serializer = IssuesListSerializer(queryset, many=True)
        return serializer.data


class CommentsListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = ['id', 'description', 'issue_id', 'author_user_id', 'created_time']
        read_only_fields = ['issue_id', 'author_user_id']


class CommentsDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = ['id', 'description', 'issue_id', 'author_user_id', 'created_time']
