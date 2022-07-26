from django.db import models
from authentication.models import User


class Projects(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    TYPE_CHOICES = [
        ('BACK_END', 'back-end'),
        ('FRONT_END', 'front-end'),
        ('IOS', 'iOS'),
        ('ANDROID', 'Android')
    ]
    type = models.CharField(max_length=128,
                            choices=TYPE_CHOICES,
                            )
    author_user_id = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return f"{self.title} ({self.id})"


class Contributors(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE)
    project = models.ForeignKey(
        to=Projects,
        on_delete=models.CASCADE)
    PERMISSION_CHOICES = [
        ('AUTHOR', 'Author'),
        ('CONTRIBUTOR', 'Contributor'),
    ]
    role = models.CharField(max_length=128,
                            choices=PERMISSION_CHOICES,
                            )

    class Meta:
        unique_together = ('user', 'project',)


class Issues(models.Model):
    title = models.CharField(max_length=128)
    desc = models.CharField(max_length=2048)
    TAG_CHOICES = [
        ('BUG', 'Bug'),
        ('IMPROVEMENT', 'Amélioration'),
        ('TASK', 'Tâche')
    ]
    tag = models.CharField(max_length=128,
                           choices=TAG_CHOICES,)
    PRIORITY_LEVEL = [
        ('LOW', 'Faible'),
        ('MEDIUM', 'Moyenne'),
        ('HIGH', 'Elevée')
    ]
    priority = models.CharField(max_length=128,
                                choices=PRIORITY_LEVEL,)
    STATUS = [
        ('TO_DO', 'A faire'),
        ('IN PROGRESS', 'En cours'),
        ('CLOSED', 'Terminé')
    ]
    status = models.CharField(max_length=128,
                              choices=STATUS,
                              default='TO_DO')
    project_id = models.ForeignKey(
        to=Projects,
        on_delete=models.CASCADE,
        related_name="issues")
    author_user_id = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="author"
    )
    assignee_user_id = models.ForeignKey(
        to=User,
        default=author_user_id,
        on_delete=models.CASCADE,
        related_name="assignee"
    )
    created_time = models.DateTimeField(auto_now_add=True)


class Comments(models.Model):
    description = models.CharField(max_length=2048)
    author_user_id = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE)
    issue_id = models.ForeignKey(
        to=Issues,
        on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
