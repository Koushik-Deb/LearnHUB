# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pdf', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='pdfsong',
            old_name='audio_file',
            new_name='pdf_file',
        ),
        migrations.RenameField(
            model_name='pdfsong',
            old_name='song_title',
            new_name='pdf_title',
        ),
    ]
