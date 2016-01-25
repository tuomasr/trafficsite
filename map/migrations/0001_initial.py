# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LAMObs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lamid', models.IntegerField()),
                ('timestamp', models.IntegerField()),
                ('trafficvol1', models.IntegerField()),
                ('trafficvol2', models.IntegerField()),
                ('avgspeed1', models.IntegerField()),
                ('avgspeed2', models.IntegerField()),
            ],
        ),
    ]
