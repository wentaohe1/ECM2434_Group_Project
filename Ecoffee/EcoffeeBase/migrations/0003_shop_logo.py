# Generated by Django 5.1.5 on 2025-02-24 12:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EcoffeeBase', '0002_customuser_delete_coffee_badge_badge_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shop',
            name='logo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
