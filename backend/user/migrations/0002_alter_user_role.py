# Generated by Django 4.1.5 on 2023-01-10 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.ManyToManyField(related_name="roles", to="user.role"),
        ),
    ]
