# Generated by Django 4.0.5 on 2022-07-23 12:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="projects",
            old_name="author",
            new_name="author_user_id",
        ),
    ]
