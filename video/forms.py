from django import forms
from django.contrib.auth.models import User

from .models import VideoAlbum, VideoSong


class AlbumForm(forms.ModelForm):

    class Meta:
        model = VideoAlbum
        fields = ['artist', 'album_title', 'genre', 'album_logo']


class SongForm(forms.ModelForm):

    class Meta:
        model = VideoSong
        fields = ['video_title', 'video_file']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
