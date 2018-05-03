from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .forms import AlbumForm, SongForm, UserForm
from .models import Album, Song
from bs4 import BeautifulSoup
from html.parser import HTMLParser
import requests
from selenium import webdriver

AUDIO_FILE_TYPES = ['wav', 'mp3', 'ogg']
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
                return render(request, 'music/create_album.html', context)
            album.save()
            return render(request, 'music/detail.html', {'album': album})
        context = {
            "form": form,
        }
        return render(request, 'music/create_album.html', context)


def create_song(request, album_id):
    form = SongForm(request.POST or None, request.FILES or None)
    album = get_object_or_404(Album, pk=album_id)
    if form.is_valid():
        albums_songs = album.song_set.all()
        for s in albums_songs:
            if s.song_title == form.cleaned_data.get("song_title"):
                context = {
                    'album': album,
                    'form': form,
                    'error_message': 'You already added that song',
                }
                return render(request, 'music/create_song.html', context)
        song = form.save(commit=False)
        song.album = album
        song.audio_file = request.FILES['audio_file']
        file_type = song.audio_file.url.split('.')[-1]
        file_type = file_type.lower()
        if file_type not in AUDIO_FILE_TYPES:
            context = {
                'album': album,
                'form': form,
                'error_message': 'Audio file must be WAV, MP3, or OGG',
            }
            return render(request, 'music/create_song.html', context)

        song.save()
        return render(request, 'music/detail.html', {'album': album})
    context = {
        'album': album,
        'form': form,
    }
    return render(request, 'music/create_song.html', context)


def delete_album(request, album_id):
    album = Album.objects.get(pk=album_id)
    album.delete()
    albums = Album.objects.filter(user=request.user)
    return render(request, 'music/index.html', {'albums': albums})


def delete_song(request, album_id, song_id):
    album = get_object_or_404(Album, pk=album_id)
    song = Song.objects.get(pk=song_id)
    song.delete()
    return render(request, 'music/detail.html', {'album': album})


def detail(request, album_id):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        user = request.user
        album = get_object_or_404(Album, pk=album_id)
        return render(request, 'music/detail.html', {'album': album, 'user': user})


def favorite(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    try:
        if song.is_favorite:
            song.is_favorite = False
        else:
            song.is_favorite = True
        song.save()
    except (KeyError, Song.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def favorite_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        if album.is_favorite:
            album.is_favorite = False
        else:
            album.is_favorite = True
        album.save()
    except (KeyError, Album.DoesNotExist):
        return JsonResponse({'success': False})
    else:
        return JsonResponse({'success': True})


def index(request):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        #albums = Album.objects.filter(user=request.user)
        albums = Album.objects.all()
        song_results = Song.objects.all()
        query = request.GET.get("q")
        if query:
            albums = albums.filter(
                Q(album_title__icontains=query) |
                Q(artist__icontains=query)
            ).distinct()
            song_results = song_results.filter(
                Q(song_title__icontains=query)
            ).distinct()
            return render(request, 'music/index.html', {
                'albums': albums,
                'songs': song_results,
            })
        else:
            return render(request, 'music/index.html', {'albums': albums})


def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'music/login.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'albums': albums})
            else:
                return render(request, 'music/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'music/login.html', {'error_message': 'Invalid login'})
    return render(request, 'music/login.html')


def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                albums = Album.objects.filter(user=request.user)
                return render(request, 'music/index.html', {'albums': albums})
    context = {
        "form": form,
    }
    return render(request, 'music/register.html', context)


def songs(request, filter_by):
    if not request.user.is_authenticated():
        return render(request, 'music/login.html')
    else:
        try:
            song_ids = []
            #for album in Album.objects.filter(user=request.user):
            for album in Album.objects.all():
                for song in album.song_set.all():
                    song_ids.append(song.pk)
            users_songs = Song.objects.filter(pk__in=song_ids)
            if filter_by == 'favorites':
                users_songs = users_songs.filter(is_favorite=True)
        except Album.DoesNotExist:
            users_songs = []
        return render(request, 'music/songs.html', {
            'song_list': users_songs,
            'filter_by': filter_by,
        })

#
# def search(request):
#     search_item = 'avengers'  ## search query
#     url = "https://www.google.com/search?q=" + search_item
#
#     response = requests.get(url)
#     # "https://www.yellowpages.com/los-angeles-ca/cofee?g=los%20angeles%2C%20ca&q=coffee
#     soup = BeautifulSoup(response.content)
#     # print(soup.prettify())
#     soup = BeautifulSoup(soup.text, "lxml")
#     # for link in soup.find_all("a"):
#     print(soup.find_all("div.g"))
#     return render(request, 'music/searchresult.html')


def search(request):
    search_term = request.GET.get("query")
    url = "https://www.startpage.com"
    browser = webdriver.PhantomJS(executable_path="/Users/HP/Downloads/Compressed/phantomjs-2.1.1-windows/bin/phantomjs.exe")
    #browser = webdriver.Chrome(executable_path="/Users/HP/Downloads/Compressed/chromedriver.exe")
    browser.get(url)
    #bs_obj = BeautifulSoup(browser.page_source,'html.parser')
    search_box = browser.find_element_by_id("query")
    search_box.send_keys(search_term)
    search_box.submit()
    try:
        links = browser.find_elements_by_xpath("//ol[@class='web_regular_results']//h3//a")
    except:
        links = browser.find_elements_by_xpath("//h3//a")
    results = []
    for link in links:
        href = link.get_attribute("href")
        text = link.get_attribute("text")
        print(text)
        print(href)
        results.append(text)
        results.append(href)
    browser.close()
    my_dict = {}
    i=0
    for i in range(len(results)):
        my_dict[i] = results[i]
    print(my_dict)
    return render(request,'music/searchresult.html',{'my_dict':my_dict})
# search("dog")
#     def __init__(self, search, page=0):
#         self.search = search
#         self.page = page
#         self.url = f'https://www.google.com/search?q={self.search}\
#                     &ei=m3w9WuyXNJHMwALelovwAQ&start={str(self.page)+"0"}&sa=N&biw=848&bih=972'
#         self.result()
#
#     def result(self):
#         browser = webdriver.PhantomJS(executable_path="/Users/HP/Downloads/Compressed/phantomjs-2.1.1-windows/bin/phantomjs.exe")
#         browser.get(self.url)
#         soup = BeautifulSoup(browser.page_source, 'lxml')
#         name_link = soup.find_all('h3', class_='r')
#         link = soup.find_all('cite')
#         for n_link, l in zip(name_link, link):
#             print(f'{n_link.text}\n{l.text}')
#             print('---------')
#
#
# if __name__ == '__main__':
#     search('python forum')