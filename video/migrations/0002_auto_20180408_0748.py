# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('video', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='videosong',
            old_name='audio_file',
            new_name='video_file',
        ),
        migrations.RenameField(
            model_name='videosong',
            old_name='song_title',
            new_name='video_title',
        ),
    ]
