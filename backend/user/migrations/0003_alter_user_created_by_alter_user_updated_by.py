# Generated by Django 4.1.5 on 2023-01-12 06:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0002_alter_user_role"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="created_by",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="create_user",
                to="user.user",
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="updated_by",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="update_user",
                to="user.user",
            ),
        ),
    ]