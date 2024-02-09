from django.db import models


class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Album(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    release_date = models.DateField()
    genre = models.CharField(max_length=50)

    search_fields = ("title", "genre")

    def __str__(self):
        return self.title


class Song(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    duration = models.IntegerField(help_text="Duration in seconds")
    lyrics = models.TextField(blank=True)

    search_fields = ("title", "lyrics")

    def __str__(self):
        return self.title
