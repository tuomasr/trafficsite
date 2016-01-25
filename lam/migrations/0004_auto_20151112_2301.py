# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lam', '0003_lamfcast'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lamfcast',
            name='trafficvol1',
            field=models.FloatField(),
        ),
    ]
