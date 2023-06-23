from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre, User
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import AuthorModelForm, BookModelForm, GenreModelForm, BookInstanceModelForm, RenewBookForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.views.generic.edit import UpdateView, DeleteView


# Code qui va être utilisé pour l'affichage de la page. L'équivalent du controlleur dans Laravel/Symfony
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()

    # Va compter les visites pour CHAQUE utilisateur indépendamment les uns des autres. La variable num_visits regarde si la session a déjà une valeur et lui attribue le chiffre 0 si ce n'est pas déjà le cas.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
        'num_visits': num_visits,
    }

    return render(request, 'index.html', context=context)


# CREATE
@login_required(login_url='/accounts/login/')
def create_user(request):
    """
    # Créer un utilisateur
    user = User.objects.create_user('myusername', 'myemail@crazymail.com', 'mypassword')

    # Modifier certains champs
    user.first_name = 'Tyrone'
    user.last_name = 'Citizen'

    # Sauvegarder l'utilisateur/les modifications
    user.save()
    """

    # A créer plus tard
    return render(request, 'users/user_create_update.html')


@permission_required('catalog.create_author', raise_exception=True)
def create_author(request):

    form = AuthorModelForm()

    if request.method == 'POST':
        form = AuthorModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'authors/author_create_update.html', {'form': form})


def create_book(request):

    form = BookModelForm()

    if request.method == 'POST':
        form = BookModelForm(request.POST)

        if form.is_valid():
            #form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'books/book_create_update.html', {'form': form})


def create_book_instance(request):

    form = BookInstanceModelForm()

    if request.method == 'POST':
        form = BookInstanceModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'books_instances/book_instance_create_update.html',
                  {'form': form})


def create_genre(request):

    form = GenreModelForm()

    if request.method == 'POST':
        form = GenreModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'genres/genre_create_update.html', {'form': form})


# READ
# Autre façon de retourner des résultats dans un template. Autre façon également de bloquer une page aux utilisateurs-non connectés. Les Mixins sont à utiliser pour les views de type "class".
class BookListView(PermissionRequiredMixin, LoginRequiredMixin,
                   generic.ListView):
    login_url = '/login/'
    permission_required = 'catalog.create_author'
    model = Book
    context_object_name = 'book_list'  # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='one')[:5] # Get and return 5 books containing the title one
    queryset = Book.objects.all()
    # Gère la logique de la pagination. L'affichage est quant à lui géré par le template associé (en l'occurence, le template "base_generic").
    paginate_by = 3
    template_name = 'books/books_list.html'  # Specify your own template name/location


# Classe d'un livre.
class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def post(self, request, pk):
      return_book(self, request, pk)
      
      return HttpResponseRedirect(self.request.path_info)


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'books/book_instance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return (BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back'))


# UPDATE
class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'authors/author_create_update.html'


class BookUpdate(UpdateView):
    model = Book
    fields = ['title', 'summary']
    template_name = 'books/book_create_update.html'


class BookInstanceUpdate(UpdateView):
    model = BookInstance
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = 'books_instances/book_instance_create_update.html'


class GenreUpdate(UpdateView):
    model = Genre
    fields = ['name']
    template_name = 'genres/genre_create_update.html'


def return_book(self, request, pk):
    if request.POST.get('borrow_book'):
        user_id = request.POST.get('user_id')
        book_instance_id = request.POST.get('copy_id')

        book_instance = get_object_or_404(BookInstance, pk=book_instance_id)
        user = get_object_or_404(User, pk=user_id)

        book_instance.borrower = user
        book_instance.status = 'o'
        book_instance.due_back = datetime.date.today() + datetime.timedelta(
            weeks=3)
        book_instance.save()

    if request.POST.get('return_book'):
        book_instance_id = request.POST.get('copy_id')

        book_instance = get_object_or_404(BookInstance, pk=book_instance_id)

        book_instance.borrower = None
        book_instance.status = 'a'
        book_instance.due_back = None
        book_instance.save()


@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book(request, pk):
    """View function for renewing a specific BookInstance."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # S'il s'agit d'une requête POST, traiter les données du formulaire.
    if request.method == 'POST':

        # Créer une instance de formulaire et la peupler avec des données récupérées dans la requête (liaison) :
        form = RenewBookForm(request.POST)

        # Vérifier que le formulaire est valide :
        if form.is_valid():
            # Traiter les données dans form.cleaned_data tel que requis (ici on les écrit dans le champ de modèle due_back) :
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # Rediriger vers une nouvelle URL :
            return HttpResponseRedirect(reverse('all-borrowed'))

    proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
    form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'books/book_renew.html', context)


# DELETE
# Cette nature de classe (DeleteView) reprend ce qui se fait dans le site d'administration. Existe en version CreateView et UpdateView
class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'authors/author_confirm_delete.html'


class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'authors/book_confirm_delete.html'


class BookInstanceDelete(DeleteView):
    model = BookInstance
    success_url = reverse_lazy('books_instances')
    template_name = 'books_instances/book_instance_confirm_delete.html'


class GenreDelete(DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    template_name = 'genres/genre_confirm_delete.html'
