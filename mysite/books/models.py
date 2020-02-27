from django.db import models
import datetime
from django.utils import timezone

# Create your models here.


class Publisher(models.Model):
    name = models.CharField(max_length=30)
    address = models.CharField(max_length=90)
    city = models.CharField(max_length=60)
    state_province = models.CharField(max_length=30)
    country = models.CharField(max_length=50)
    website = models.URLField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Author(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=40)
    email = models.EmailField(blank=True)

    def __str__(self):
        return u"%s %s" % (self.first_name, self.last_name)


class BookManager(models.Manager):
    def title_count(self, keyword):
        return self.filter(title__icontains=keyword).count()


class MortimerManager(models.Manager):
    def get_queryset(self):
        return (
            super(DahlBookManager, self)
            .get_queryset()
            .filter(author="Mortimer Scollan")
        )


class Book(models.Model):
    title = models.CharField(max_length=100)
    authors = models.ManyToManyField(Author)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
    publication_date = models.DateField(auto_now=True)
    num_pages = models.IntegerField(blank=True, null=True)
    objects = models.Manager()
    dahl_objects = MortimerManager()

    def __str__(self):
        return self.title

    def recent_publication(self):
        return self.publication_date >= timezone.now().date() - datetime.timedelta(
            weeks=8
        )
