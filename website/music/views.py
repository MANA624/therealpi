from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from .models import Album, Song


# Create your views here.
def index(request):
    all_albums = Album.objects.all()
    context = {'all_albums': all_albums}
    return render(request, 'music/index.html', context)


def detail(request, album_id):
    # all_albums = Album.objects.all()
    # context = {'all_albums': all_albums}
    # try:
    #     album = Album.objects.get(pk=album_id)
    # except Album.DoesNotExist:
    #     raise Http404("You picked a bad site")
    # This line is the same as the above lines
    album = get_object_or_404(Album, pk=album_id)
    return render(request, 'music/detail.html', {'album': album})


def favorite(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    try:
        selected_song = album.song_set.get(pk=request.POST['song'])
    except (KeyError, Song.DoesNotExist):
        return render(request, 'music/detail.html', {'album': album, 'error_message': "You selected nada!"})
    else:
        for song in album.song_set.all():
            song.is_favorite = False
            song.save()

        selected_song.is_favorite = True
        selected_song.save()
        return render(request, 'music/detail.html', {'album': album})


def not_found(request):
    return HttpResponse("<h1>The page you're looking for is not valid!</h1>")

