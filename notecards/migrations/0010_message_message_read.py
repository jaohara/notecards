# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-31 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notecards', '0009_auto_20170130_2331'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='message_read',
            field=models.BooleanField(default=False),
        ),
    ]
