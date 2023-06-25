from django.test import TestCase
from django.urls import reverse
import datetime
from django.utils import timezone
from django.contrib.auth.models import User, Permission
from catalog.models import Author, BookInstance, Book, Genre


class AuthorListViewTest(TestCase):
    def setUp(self):
        # Create 13 authors for pagination tests
        number_of_authors = 13

        for author_id in range(number_of_authors):
            # Pour rappel, le 'f' permet d'interpréter les variables dans la chaine de caractères.
            Author.objects.create(
                first_name=f'Dominique {author_id}',
                last_name=f'Surname {author_id}',
            )

        test_user = User.objects.create_user(username="Salaah",
                                             email="sokhona.salaha@gmail.com",
                                             password="Salsdu19")
        # Give test_user2 permission to renew books.
        permission = Permission.objects.get(name='Ajouter un nouvel auteur')
        test_user.user_permissions.add(permission)
        test_user.save()

    def test_view_url_accessible_by_name(self):
        login = self.client.login(username='Salaah', password='Salsdu19')
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        login = self.client.login(username='Salaah', password='Salsdu19')
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'authors/authors_list.html')

    def test_pagination_is_ten(self):
        login = self.client.login(username='Salaah', password='Salsdu19')
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'] == True)
        self.assertEqual(len(response.context['authors_list']), 10)


class LoanedBookInstancesByUserListViewTest(TestCase):
    def setUp(self):
        # Create two users
        test_user1 = User.objects.create_user(username='testuser1',
                                              password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2',
                                              password='2HJ1vRV0Z&3iD')

        test_user1.save()
        test_user2.save()

        # Create a book
        test_author = Author.objects.create(first_name='John',
                                            last_name='Smith')
        test_genre = Genre.objects.create(name='Fantasy')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='ABCDEFG',
            author=test_author,
        )

        # Create genre as a post-step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(
            genre_objects_for_book
        )  # Direct assignment of many-to-many types not allowed.
        test_book.save()

        # Create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(
                days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response,
                             '/accounts/login/?next=/catalog/mybooks/')

    def test_only_borrowed_books_in_list(self):
        login = self.client.login(username='testuser1',
                                  password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        # Vérifie si mon utilisateur est connecté. Str() renvoie l'objet sous forme de string
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        # Check that initially we don't have any books in list (none on loan)
        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # Now change all books to be on loan
        books = BookInstance.objects.all()[:10]

        for book in books:
            book.status = 'o'
            book.save()

        # Check that now we have borrowed books in the list
        response = self.client.get(reverse('my-borrowed'))
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'testuser1')
        # Check that we got a response "success"
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)

        # Confirm all books belong to testuser1 and are on loan
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual(bookitem.status, 'o')
