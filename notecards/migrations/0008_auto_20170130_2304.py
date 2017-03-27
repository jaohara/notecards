# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2017-01-31 07:04
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notecards', '0007_quizresult'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quizresult',
            name='deck',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='notecards.Deck'),
        ),
        migrations.AlterField(
            model_name='quizresult',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]