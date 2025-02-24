# Generated by Django 5.1.6 on 2025-02-24 15:57

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('badgeId', models.AutoField(primary_key=True, serialize=False)),
                ('coffeeUntilEarned', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('badge_image', models.CharField(default='', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('shopId', models.AutoField(primary_key=True, serialize=False)),
                ('shopName', models.CharField(max_length=255, unique=True)),
                ('numberOfVisits', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('activeCode', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cupsSaved', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('lastActiveDateTime', models.DateTimeField(blank=True, null=True)),
                ('defaultBadgeId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EcoffeeBase.badge')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('mostRecentShopId', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EcoffeeBase.shop')),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owned', models.BooleanField(default=False)),
                ('dateTimeObtained', models.DateTimeField(blank=True, null=True)),
                ('badgeId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.customuser')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'badgeId'), name='uniqueUserBadge')],
            },
        ),
        migrations.CreateModel(
            name='UserShop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitAmounts', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('shopId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.shop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.customuser')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'shopId'), name='uniqueUserShop')],
            },
        ),
    ]
