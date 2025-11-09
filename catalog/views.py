from django.shortcuts import render
from django.views import generic

from .models import Book, BookInstance, Author,Genre

def index(request):
    """View function for home page of site."""
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors = Author.objects.count()
    num_genres = Genre.objects.count()
    num_books_with_word = Book.objects.filter(title__icontains='מלחמה').count()
  
    context = {
    'num_books': num_books,
    'num_instances': num_instances,
    'num_instances_available': num_instances_available,
    'num_authors': num_authors,
    'num_genres': num_genres,
    'num_books_with_word': num_books_with_word,
    }
    return render(request,  'catalog/index.html', context=context)
class BookListView(generic.ListView):
    model = Book
    paginate_by = 10
class BookDetailView(generic.DetailView):
    model = Book
class AuthorListView(generic.ListView):
    model = Author
    paginate_by = 10 # אפשר להוסיף גם פה מספור עמודים

class AuthorDetailView(generic.DetailView):
    model = Author