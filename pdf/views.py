from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import AlbumForm, SongForm, UserForm
from .models import PdfSong,PdfAlbum


AUDIO_FILE_TYPES = ['pdf', 'doc']
IMAGE_FILE_TYPES = ['png', 'jpg', 'jpeg']


def create_album(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        form = AlbumForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            album = form.save(commit=False)
            album.user = request.user
            album.album_logo = request.FILES['album_logo']
            file_type = album.album_logo.url.split('.')[-1]
            file_type = file_type.lower()
            if file_type not in IMAGE_FILE_TYPES:
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'Image file must be PNG, JPG, or JPEG',
                }
                return render(request, 'pdf/create_album.html', context)
            album.save()
            return render(request, 'pdf/detail.html', {'album': album})
        context = {
            "form": form,
        }
        return render(request, 'pdf/create_album.html', context)


def create_song(request, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(PdfAlbum, pk=album_id)
    if form.is_valid():
        albums_songs = album.pdfsong_set.all()
        for s in albums_songs:
            if s.pdf_title == form.cleaned_data.get("pdf_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'pdf/create_song.html', context)
        song = form.save(commit=False)
        song.album = album
        song.pdf_file = request.FILES['pdf_file']
        file_type = song.pdf_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Video file must be mp4',
            }
            return render(request, 'pdf/create_song.html', context)

        song.save()
        return render(request, 'pdf/detail.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'pdf/create_song.html', context)


def delete_album(request, album_id):
    album = PdfAlbum.objects.get(pk=album_id)
    album.delete()
    albums = PdfAlbum.objects.filter(user=request.user)
    return render(request, 'pdf/index.html', {'albums': albums})


def delete_song(request, album_id, song_id):
    album = get_object_or_404(PdfAlbum, pk=album_id)
    song = PdfSong.objects.get(pk=song_id)
    song.delete()
    return render(request, 'pdf/detail.html', {'album': album})


def detail(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        user = request.user
        album = get_object_or_404(PdfAlbum, pk=album_id)
        return render(request, 'pdf/detail.html', {'album': album, 'user': user})


def favorite(request, song_id):
    song = get_object_or_404(PdfSong, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
        song.save()
    except (KeyError, PdfSong.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_album(request, album_id):
    album = get_object_or_404(PdfAlbum, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except (KeyError, PdfAlbum.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        #albums = Album.objects.filter(user=request.user)
        albums = PdfAlbum.objects.all()
        song_results = PdfSong.objects.all()
        query = request.GET.get("q")
        if query:
            albums = albums.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(pdf_title__icontains=query)
            ).distinct()
            return render(request, 'pdf/index.html', {
                'albums': albums,
                'songs': song_results,
            })
        else:
            return render(request, 'pdf/index.html', {'albums': albums})


# def logout_user(request):
#     logout(request)
#     form = UserForm(request.POST or None)
#     context = {
#         "form": form,
#     }
#     return render(request, 'music/login.html', context)
#
#
# def login_user(request):
#     if request.method == "POST":
#         username = request.POST['username']
#         password = request.POST['password']
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 albums = VideoAlbum.objects.filter(user=request.user)
#                 return render(request, 'music/index.html', {'albums': albums})
#             else:
#                 return render(request, 'music/login.html', {'error_message': 'Your account has been disabled'})
#         else:
#             return render(request, 'music/login.html', {'error_message': 'Invalid login'})
#     return render(request, 'music/login.html')
#
#
# def register(request):
#     form = UserForm(request.POST or None)
#     if form.is_valid():
#         user = form.save(commit=False)
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user.set_password(password)
#         user.save()
#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 albums = VideoAlbum.objects.filter(user=request.user)
#                 return render(request, 'music/index.html', {'albums': albums})
#     context = {
#         "form": form,
#     }
#     return render(request, 'music/register.html', context)


def songs(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            for album in PdfAlbum.objects.filter(user=request.user):
                for song in album.pdfsong_set.all():
                    song_ids.append(song.pk)
            users_songs = PdfSong.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except PdfAlbum.DoesNotExist:
            users_songs = []
        return render(request, 'pdf/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })


