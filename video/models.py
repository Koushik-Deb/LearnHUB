from django.contrib.auth.models import Permission, User
from django.db import models


class VideoAlbum(models.Model):
    user = models.ForeignKey(User, default=1)
    artist = models.CharField(max_length=250)
    album_title = models.CharField(max_length=500)
    genre = models.CharField(max_length=100)
    album_logo = models.FileField()
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.album_title + ' - ' + self.artist


class VideoSong(models.Model):
    album = models.ForeignKey(VideoAlbum, on_delete=models.CASCADE)
    video_title = models.CharField(max_length=250)
    video_file = models.FileField(default='')
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.song_title
