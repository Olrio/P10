# Generated by Django 4.0.5 on 2022-07-17 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_issues_comments'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issues',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='projects.projects'),
        ),
    ]
