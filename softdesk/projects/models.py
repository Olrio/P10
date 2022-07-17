from django.db import models
from django.contrib.auth.models import User

class Projects(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    type = models.CharField(max_length=128)
    author = models.ForeignKey(
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


class Issues(models.Model):
    title = models.CharField(max_length=128)
    desc = models.CharField(max_length=2048)
    tag = models.CharField(max_length=128)
    priority = models.CharField(max_length=128)
    project = models.ForeignKey(
        to=Projects,
        on_delete=models.CASCADE,
        related_name="issues")
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="author"
    )
    assignee = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name="assignee"
    )
    created_time = models.DateTimeField(auto_now_add=True)



class Comments(models.Model):
    description = models.CharField(max_length=2048)
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE)
    issue = models.ForeignKey(
        to=Issues,
        on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)
