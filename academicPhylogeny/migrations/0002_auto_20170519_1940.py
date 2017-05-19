# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-19 19:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('academicPhylogeny', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PhD',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstName', models.CharField(blank=True, max_length=100, null=True)),
                ('lastName', models.CharField(blank=True, max_length=100, null=True)),
                ('year', models.IntegerField(blank=True, max_length=4, null=True)),
                ('URL_for_detail', models.CharField(max_length=200, null=True)),
                ('advisor', models.ManyToManyField(blank=True, null=True, related_name='_phd_advisor_+', to='academicPhylogeny.PhD')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='academicPhylogeny.school')),
                ('specialization', models.ManyToManyField(blank=True, null=True, to='academicPhylogeny.specialization')),
            ],
            options={
                'ordering': ['lastName'],
                'db_table': 'PhD',
                'verbose_name_plural': 'PhDs',
            },
        ),
        migrations.AlterUniqueTogether(
            name='phd',
            unique_together=set([('firstName', 'lastName')]),
        ),
    ]
