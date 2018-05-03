from django import forms
from django.contrib.auth.models import User

from .models import StorageAlbum, StorageSong


class AlbumForm(forms.ModelForm):

    class Meta:
        model = StorageAlbum
        fields = ['artist', 'album_title', 'genre', 'album_logo']


class SongForm(forms.ModelForm):

    class Meta:
        model = StorageSong
        fields = ['song_title', 'audio_file']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
