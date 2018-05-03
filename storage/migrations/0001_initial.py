# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StorageAlbum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('artist', models.CharField(max_length=250)),
                ('album_title', models.CharField(max_length=500)),
                ('genre', models.CharField(max_length=100)),
                ('album_logo', models.FileField(upload_to=b'')),
                ('is_favorite', models.BooleanField(default=False)),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StorageSong',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('song_title', models.CharField(max_length=250)),
                ('audio_file', models.FileField(default=b'', upload_to=b'')),
                ('is_favorite', models.BooleanField(default=False)),
                ('album', models.ForeignKey(to='storage.StorageAlbum')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
