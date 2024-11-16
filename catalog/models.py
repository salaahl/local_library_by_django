from django.db import models
from django.urls import reverse  # Cette fonction est utilisée pour formater les URL
import uuid  # Ce module est nécessaire à la gestion des identifiants unique (RFC 4122) pour les copies des livres
from django.contrib.auth.models import User
from datetime import date


# Model Genre
class Permission(models.Model):
    """Cet objet représente les permissions."""
    class Meta:
        # Création d'une permission. Elle sera - après migration - assignable à un groupe d'utilisateurs et la logique se fera ensuite dans le template, dans l'objet "perms" (qui est envoyé par défaut au template) - "{% if perms.catalog.read_authors_and_books %}")
        permissions = (("read_authors_and_books",
                        "Accès au listing des auteurs et des livres."), )

    def __str__(self):
        """Cette fonction est obligatoirement requise par Django.
           Elle retourne une chaîne de caractère pour identifier l'instance de la classe d'objet. L'appel se fait avec la fonction str(monModel)"""
        return self.name


# Model Genre
class Genre(models.Model):
    name = models.CharField(
        max_length=200, help_text='Enter a book genre (e.g. Science Fiction)')

    def __str__(self):
        return self.name


# Model Book
class Book(models.Model):
    """Cet objet représente un livre (mais ne traite pas les copies présentes en rayon)."""
    title = models.CharField(max_length=200)

    #  Un livre a un seul auteur, mais un auteur a écrit plusieurs livres.
    author = models.ForeignKey('Author', on_delete=models.CASCADE, null=True)

    summary = models.TextField(
        max_length=1000, help_text='Enter a brief description of the book')
    isbn = models.CharField(
        'ISBN',
        max_length=13,
        help_text=
        '13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>'
    )

    #  un livre peut avoir plusieurs genres littéraire et réciproquement.
    genre = models.ManyToManyField(Genre,
                                   help_text='Select a genre for this book')

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """Returns the url to access a particular book instance."""
        return reverse('book-detail', args=[str(self.id)])

    def display_genre(self):
        return ', '.join(genre.name for genre in self.genre.all()[:3])

    display_genre.short_description = 'Genre'


# Model BookInstance
class BookInstance(models.Model):
    """Cet objet permet de modéliser les copies d'un ouvrage (i.e. qui peut être emprunté)."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text='Unique ID for this particular book across whole library')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    imprint = models.CharField(max_length=200)
    pdf_file = models.FileField(upload_to='book_pdfs/', blank=True, null=True)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User,
                                 on_delete=models.SET_NULL,
                                 null=True,
                                 blank=True)

    LOAN_STATUS = (
        ('m', 'Problème sur document'),
        ('o', 'Emprunté'),
        ('a', 'Disponible'),
        ('r', 'Réservé'),
    )

    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        blank=True,
        default='m',
        help_text='Book availability',
    )

    class Meta:
        ordering = ['due_back']

    @property
    def is_overdue(self):
        """Determines if the book is overdue based on due date and current date."""
        return bool(self.due_back and date.today() > self.due_back)

    def __str__(self):
        return f'{self.id} ("{self.book.title}" - {self.book.author})'


# Model Auteur
class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        """Returns the url to access a particular author instance."""
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        """Retourne le nom et prénom de l'auteur."""
        return f'{self.last_name}, {self.first_name}'
