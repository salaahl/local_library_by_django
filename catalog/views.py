import os
from django.shortcuts import render, get_object_or_404
from catalog.models import Book, Author, BookInstance, Genre, User
from django.views import generic
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from .forms import UserModelForm, AuthorModelForm, BookModelForm, GenreModelForm, BookInstanceModelForm, RenewBookForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import datetime
from django.views.generic.edit import UpdateView, DeleteView
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_mail(from_email, to_emails, subject, html_content):
    """
    Easy wrapper for sending a single message to a recipient list. All members
    of the recipient list will see the other recipients in the 'To' field.

    If auth_user is None, use the EMAIL_HOST_USER setting.
    If auth_password is None, use the EMAIL_HOST_PASSWORD setting.

    Note: The API for this method is frozen. New code wanting to extend the
    functionality should use the EmailMessage class directly.
    """
    message = Mail(
    from_email=from_email,
    to_emails=to_emails,
    subject=subject,
    html_content=html_content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)


def index(request):
    """View function for home page of site."""

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

    # send_mail('sokhona.salaha@gmail.com', 'salsdu19@gmail.com', 'Sujet : Votre compte.', '<strong>Message : Compte créé</strong>')

    return render(request, 'index.html', context=context)


# CREATE
# Le paramètre indique le chemin sur lequel rediriger l'utilisateur s'il n'est pas connecté
@login_required(login_url='/accounts/login/')
@permission_required('catalog.can_add_user', raise_exception=True)
def create_user(request):

    form = UserModelForm()

    if request.method == 'POST':
        form = UserModelForm(request.POST)

        if form.is_valid():
            form.save()
            send_mail(
              'salsdu19@gmail.com', 
              'Sujet : Votre compte.', 
              '<strong>Message : Compte créé</strong>'
            )

            return HttpResponseRedirect(reverse('index'))

    # A créer plus tard
    return render(request, 'create_update_form.html', {'form': form})


@login_required(login_url='/accounts/login/')
@permission_required('catalog.can_add_author', raise_exception=True)
def create_author(request):

    form = AuthorModelForm()

    if request.method == 'POST':
        form = AuthorModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'create_update_form.html', {'form': form})


@login_required(login_url='/accounts/login/')
@permission_required('catalog.can_add_book', raise_exception=True)
def create_book(request):

    form = BookModelForm()

    if request.method == 'POST':
        form = BookModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'create_update_form.html', {'form': form})


@login_required(login_url='/accounts/login/')
@permission_required('catalog.can_add_book_instance', raise_exception=True)
def create_book_instance(request):

    form = BookInstanceModelForm()

    if request.method == 'POST':
        form = BookInstanceModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'create_update_form.html',
                  {'form': form})


@login_required(login_url='/accounts/login/')
@permission_required('catalog.can_add_genre', raise_exception=True)
def create_genre(request):

    form = GenreModelForm()

    if request.method == 'POST':
        form = GenreModelForm(request.POST)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('index'))

    return render(request, 'create_update_form.html', {'form': form})


# READ
# Les class sont également une façon de retourner des résultats dans un template.
class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'authors_list'  # your own name for the list as a template variable
    # queryset = Book.objects.filter(title__icontains='one')[:5] # Get and return 5 books containing the title one
    # Le signe "-" indique à Django de sortir les résultats par ordre descendant
    queryset = Author.objects.all().order_by('-id')
    # Gère la logique de la pagination. L'affichage est quant à lui géré par le template associé (en l'occurence, le template "base_generic").
    paginate_by = 10
    template_name = 'authors/authors_list.html'


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'books_list'
    queryset = Book.objects.all()
    paginate_by = 1
    template_name = 'books/books_list.html'


class BookDetailView(generic.DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def post(self, request, pk):
        if request.POST.get('borrow_book'):
            borrow_book(self, request)
        elif request.POST.get('return_book'):
            return_book(self, request)

        # Redirige vers l'URL d'origine
        return HttpResponseRedirect(self.request.path_info)


class AuthorDetailView(generic.DetailView):
    model = Author
    template_name = 'authors/author_detail.html'


# Les Mixins sont une autre façon de bloquer une page aux utilisateurs selon conditions (ici, que l'utilisateur soit connecté). Ils sont à utiliser pour les views de type "class".
class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    login_url = '/accounts/login/'
    model = BookInstance
    context_object_name = 'borrows_list'
    template_name = 'users/user_list_borrows.html'
    paginate_by = 10

    def get_queryset(self):
        return (BookInstance.objects.filter(borrower=self.request.user).filter(
            status__exact='o').order_by('due_back'))


# UPDATE
class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_change_author'
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = '_create_update_form.html'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_change_book'
    model = Book
    fields = ['title', 'summary']
    template_name = '_create_update_form.html'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_change_book_instance'
    model = BookInstance
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    template_name = '_create_update_form.html'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = 'catalog.can_change_genre'
    model = Genre
    fields = ['name']
    template_name = '_create_update_form.html'


def borrow_book(self, request):
    user_id = request.POST.get('user_id')
    book_instance_id = request.POST.get('copy_id')

    book_instance = get_object_or_404(BookInstance, pk=book_instance_id)
    user = get_object_or_404(User, pk=user_id)

    book_instance.borrower = user
    book_instance.status = 'o'
    book_instance.due_back = datetime.date.today() + datetime.timedelta(
        weeks=3)
    book_instance.save()


def return_book(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    if request.method == 'POST':
        book_instance.borrower = None
        book_instance.status = 'a'
        book_instance.due_back = None
        book_instance.save()

        return HttpResponseRedirect(request.GET.get('next'))

    return render(request, 'books_instances/book_instance_confirm_return.html',
                  {'book_instance': book_instance})


@login_required
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
class AuthorDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_delete_author'
    model = Author
    success_url = reverse_lazy('authors')
    template_name = 'authors/delete_form.html'


class BookDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_delete_book'
    model = Book
    success_url = reverse_lazy('books')
    template_name = 'authors/delete_form.html'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_delete_book_instance'
    model = BookInstance
    success_url = reverse_lazy('books_instances')
    template_name = 'authors/delete_form.html'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    permission_required = 'catalog.can_delete_genre'
    model = Genre
    success_url = reverse_lazy('genres')
    template_name = 'authors/delete_form.html'
