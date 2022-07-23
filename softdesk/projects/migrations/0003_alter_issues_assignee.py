# Generated by Django 4.0.5 on 2022-07-23 13:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('projects', '0002_rename_author_projects_author_user_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issues',
            name='assignee',
            field=models.ForeignKey(default=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL), on_delete=django.db.models.deletion.CASCADE, related_name='assignee', to=settings.AUTH_USER_MODEL),
        ),
    ]
