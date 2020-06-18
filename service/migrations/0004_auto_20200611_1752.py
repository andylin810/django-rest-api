# Generated by Django 3.0.7 on 2020-06-11 21:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0003_auto_20200611_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bills', to=settings.AUTH_USER_MODEL),
        ),
    ]