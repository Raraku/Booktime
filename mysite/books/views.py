from django.shortcuts import render
from django.shortcuts import HttpResponse
from books.models import Book
from django.views.generic import ListView, DetailView
from books.models import Publisher, Book

# Create your views here.


def search_form(request):
    return render(request, "search_form.html")


def search(request):
    if "q" in request.GET and request.GET["q"]:
        q = request.GET["q"]
        books = Book.objects.filter(title__icontains=q)
        return render(request, "search_results.html", {"books": books, "query": q})
    else:
        return HttpResponse("Please submit a search term")


class PublisherList(ListView):
    model = Publisher


class PublisherDetail(DetailView):
    model = Publisher

    def get_context_data(self, **kwargs):
        context = super(PublisherDetail, self).get_context_data(**kwargs)
        context["book_list"] = Book.objects.all()
