from django.contrib.auth.models import Permission, User
from django.db import models


class PdfAlbum(models.Model):
    user = models.ForeignKey(User, default=1)
    artist = models.CharField(max_length=250)
    album_title = models.CharField(max_length=500)
    genre = models.CharField(max_length=100)
    album_logo = models.FileField()
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.album_title + ' - ' + self.artist


class PdfSong(models.Model):
    album = models.ForeignKey(PdfAlbum, on_delete=models.CASCADE)
    pdf_title = models.CharField(max_length=250)
    pdf_file = models.FileField(default='')
    is_favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.song_title
