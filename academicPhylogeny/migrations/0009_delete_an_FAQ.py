# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-20 00:38
from __future__ import unicode_literals

from django.db import migrations

def deleteFAQ(apps,schema_editor):
    FAQ = apps.get_model("academicPhylogeny", "frequently_asked_question")
    toDelete = FAQ.objects.get(pk=2)
    toDelete.delete()

class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0008_validate_current_PhDs'),
    ]

    operations = [
        migrations.RunPython(deleteFAQ)
    ]
