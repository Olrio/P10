# Generated by Django 4.0.5 on 2022-07-26 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_rename_assignee_issues_assignee_user_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comments',
            old_name='author',
            new_name='author_user_id',
        ),
        migrations.RenameField(
            model_name='comments',
            old_name='issue',
            new_name='issue_id',
        ),
    ]