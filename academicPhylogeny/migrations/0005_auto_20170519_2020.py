# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-19 20:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0004_phd_validated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phd',
            name='validated',
            field=models.NullBooleanField(default=False),
        ),
    ]
