# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-09-27 20:03
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0020_add_user_profile_pictures'),
    ]

    operations = [
        migrations.CreateModel(
            name='LegacyPicture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', models.ImageField(upload_to=b'')),
                ('associated_PhD', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='academicPhylogeny.PhD')),
            ],
        ),
    ]


