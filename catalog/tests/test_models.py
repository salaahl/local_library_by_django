from django.test import TestCase
from catalog.models import Genre, Book, Author

class CatalogTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
      cls.author = Author.objects.create(first_name="Salah",last_name="Sohkona", date_of_birth="1900-01-01", date_of_death="2000-01-01")
      cls.genre = Genre.objects.create(name="livre")
      cls.book = Book.objects.create(title="", summary="", isbn="")
      cls.book.author.add(cls.author)
      cls.book.genre.add(cls.genre)
      print("La méthode setUpTestData n'est appelée qu'une seule fois.")
      
    def setUp(self):
        self.genre = Genre.objects.create(name="CD")
        print("La méthode setUp est appelée autant de fois qu'il y a de méthodes.")

    def test_get_genre(self):
        """La fonction get_genre contient une erreur."""
        genreObject = Genre.objects.get(name="Vinyle")
        genreObject.name = "CD"
        genreObject.save()

    def test_get_genre_new(self):
        """La fonction get_genre_new contient une erreur."""
        genre = Genre.objects.get(name="Vinyle")
        self.assertEqual(genre.__str__(), "Vinyle")