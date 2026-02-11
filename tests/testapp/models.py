from django.db import models


class Person(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)

    global_search_fields = ("name", "bio")

    class Meta:
        ordering = ["id"]
        app_label = "testapp"

    def __str__(self):
        return self.name
