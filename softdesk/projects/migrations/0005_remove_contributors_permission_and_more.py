# Generated by Django 4.0.5 on 2022-07-17 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_alter_issues_project'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contributors',
            name='permission',
        ),
        migrations.AlterField(
            model_name='contributors',
            name='role',
            field=models.CharField(choices=[('AUTHOR', 'Author'), ('CONTRIBUTOR', 'Contributor')], max_length=128),
        ),
    ]