# Generated by Django 4.0.5 on 2022-07-20 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0006_alter_contributors_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projects',
            name='type',
            field=models.CharField(choices=[('BACK_END', 'back-end'), ('FRONT_END', 'front-end'), ('IOS', 'iOS'), ('ANDROID', 'Android')], max_length=128),
        ),
    ]