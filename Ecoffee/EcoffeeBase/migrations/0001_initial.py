# Generated by Django 5.1.5 on 2025-03-22 21:44

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
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
                ('badge_id', models.AutoField(primary_key=True, serialize=False)),
                ('coffee_until_earned', models.IntegerField(unique=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('badge_image', models.CharField(default='defaultbadge.png', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Shop',
            fields=[
                ('shop_id', models.AutoField(primary_key=True, serialize=False)),
                ('shop_name', models.CharField(max_length=255, unique=True)),
                ('number_of_visits', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('active_code', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_email_verified', models.BooleanField(default=False)),
                ('email_verification_token', models.CharField(blank=True, max_length=64, null=True)),
                ('cups_saved', models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ('last_active_date_time', models.DateTimeField(default=django.utils.timezone.now)),
                ('streak', models.IntegerField(default=1)),
                ('streak_start_day', models.DateField(default=django.utils.timezone.now)),
                ('profile_image', models.ImageField(default='profile_pics/default.png', upload_to='profile_pics')),
                ('default_badge_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EcoffeeBase.badge')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('most_recent_shop_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='EcoffeeBase.shop')),
            ],
        ),
        migrations.CreateModel(
            name='ShopUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shop_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.shop')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserBadge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_time_obtained', models.DateTimeField(blank=True, null=True)),
                ('badge_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.badge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.customuser')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'badge_id'), name='unique_user_badge')],
            },
        ),
        migrations.CreateModel(
            name='UserShop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visit_amounts', models.IntegerField(validators=[django.core.validators.MinValueValidator(0)])),
                ('shop_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.shop')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='EcoffeeBase.customuser')),
            ],
            options={
                'constraints': [models.UniqueConstraint(fields=('user', 'shop_id'), name='unique_user_shop')],
            },
        ),
    ]
