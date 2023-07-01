from django.contrib import admin
from catalog.models import Author, Genre, Book, BookInstance

# Register your models here. Façon de faire la plus basique.
# admin.site.register(Book)
# admin.site.register(Author)
admin.site.register(Genre)
# admin.site.register(BookInstance)

# Define the admin class. Tout ce qui suit est une façon detournée de faire et est liée au site d'administration.
class AuthorAdmin(admin.ModelAdmin):
  # La ligne ci-dessous modifie la façon dont les données sont affichées dans le site d'administration. La façon normale avec le "# admin.site.register(Author)" n'affiche que le titre. Avec la variable "list_display" je peux aussi afficher les autres champs renseignés.
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
  # Cette variable gère l'affichage. Chaque champ déclaré tout seul représente une ligne, les champs déclarés ensemble entre parenthèses se partagent la ligne.
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]

# Register the admin class with the associated model
admin.site.register(Author, AuthorAdmin)

# Va être utilisé dans la classe BookAdmin. admin.TabularInline (horizontal) ou admin.StackInline (vertical) son les deux modes de présentation.
class BooksInstanceInline(admin.TabularInline):
    model = BookInstance
    extra = 0
  
# Register the Admin classes for Book using the decorator. La ligne ci-dessous fais la même chose que admin.site.register(Book)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
  # display_genre est une fonction définie dans le fichier models.py. Django ne peut pas directement afficher une relation many à many (et le champ "Genre" est une relation many à many)
    list_display = ('author', 'display_genre')
  # C'est le bloc qui s'affiche en bas lors de la création d'un livre. Il va me permettre d'afficher les enregistrements de la classe "BookInstance"
    inlines = [BooksInstanceInline]

# Register the Admin classes for BookInstance using the decorator
@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
  # Cette variable génère un filtre avec les valeurs renseignées.
    list_filter = ('status', 'borrower', 'due_back')
  # Gère l'affichage à l'image de "fields" dans la classe AuthorAdmin. Par sections cette fois-ci. "Availability" (ou le "None" en début, veut dire que la section n'aura pas d'en-tête) représente l'en-tête de la section et "fields" déclare les champs à afficher.
    fieldsets = (
      (None, {
          'fields': ('book', 'imprint', 'id')
      }),
      ('Availability', {
          'fields': ('status', 'due_back','borrower')
      }),
    )