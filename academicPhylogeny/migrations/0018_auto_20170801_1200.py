# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-01 16:00
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0017_add_socialmediaposts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='socialmediaposts',
            options={'verbose_name': 'social media post', 'verbose_name_plural': 'social media posts'},
        ),
        migrations.AddField(
            model_name='userprofile',
            name='alert_email_sent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='research_blurb',
            field=models.TextField(blank=True, max_length=2000, null=True, verbose_name='Describe your research program (2000 characters max)'),
        ),
    ]
