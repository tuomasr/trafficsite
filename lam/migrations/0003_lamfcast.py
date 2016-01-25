# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lam', '0002_lamstation'),
    ]

    operations = [
        migrations.CreateModel(
            name='LAMFcast',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lamid', models.IntegerField()),
                ('timestamp', models.IntegerField()),
                ('trafficvol1', models.IntegerField()),
            ],
        ),
    ]
