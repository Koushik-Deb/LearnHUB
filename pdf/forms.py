from django import forms
from django.contrib.auth.models import User

from .models import PdfAlbum, PdfSong


class AlbumForm(forms.ModelForm):

    class Meta:
        model = PdfAlbum
        fields = ['artist', 'album_title', 'genre', 'album_logo']


class SongForm(forms.ModelForm):

    class Meta:
        model = PdfSong
        fields = ['pdf_title', 'pdf_file']


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
