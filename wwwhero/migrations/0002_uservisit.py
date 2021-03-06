# Generated by Django 3.1.4 on 2020-12-27 20:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('wwwhero', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserVisit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('view', models.PositiveSmallIntegerField(default=0)),
                ('url', models.CharField(max_length=200)),
                ('method', models.CharField(max_length=8)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'url', 'method')},
            },
        ),
    ]
