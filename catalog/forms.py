from django.forms import ModelForm
from catalog.models import Book, Author, BookInstance, Genre
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext as _
import re
import datetime


class BookModelForm(ModelForm):
    def check_isbn(self):
        data = self.cleaned_data["isbn"]
        if len(data) != 13:
            raise ValidationError(_("Le format de l'ISBN est incorrect."),
                                  code="invalid")

        return data

    def summary_size(self):
        data = self.cleaned_data["summary"]
        if len(data) > 255:
            raise ValidationError(
                _("La description ne doit pas dépasser 255 caractères."),
                code="invalid")

        return data

    class Meta:
        model = Book
        fields = ['title', 'summary', 'isbn', 'author']
        labels = {
            'title': ('titre'),
            'summary': ('Description'),
            'author': ('Auteur')
        }
        help_texts = {'summary': ('255 caractères maximum.')}


class AuthorModelForm(ModelForm):
    def clean_date(self):
        data = self.cleaned_data["date_of_birth"]

        def use_regex(input_text):
            pattern = re.compile(r"\d\d/\d\d/\d\d\d\d", re.IGNORECASE)
            return bool(pattern.match(input_text))

        if bool(use_regex(data)) is False:
            raise ValidationError(
                _("Erreur. La date doit être au format JJ/MM/AAAA."),
                code="invalid")

        return data

    class Meta:
        model = Author
        fields = ['last_name', 'first_name', 'date_of_birth', 'date_of_death']
        # Redéfinition du label et du help_texts
        labels = {
            'last_name': ('Nom'),
            'first_name': ('Prénom'),
            'date_of_birth': ('Date de naissance'),
            'date_of_death': ('Date de décès')
        }
        help_texts = {'date_of_death': ('Si date de décès.')}


class GenreModelForm(forms.Form):
    name = forms.CharField(label="Nom", help_text="Entrez un nom de genre.")

    def clean_name(self):
        data = self.cleaned_data['name']

        if len(data) < 2:
            raise ValidationError(_("Erreur. Le nom de genre est trop court."),
                                  code="invalid")

        return data


class BookInstanceModelForm(ModelForm):
    class Meta:
        model = BookInstance
        fields = ['imprint', 'due_back', 'status', 'book']
        labels = {
            'imprint': ('Date d\'emprunt'),
            'due_back': ('Date de retour'),
            'status': ('Statut'),
            'book': ('Livre')
        }
        help_texts = {'status': ('Disponibilité du livre')}


class RenewBookForm(forms.Form):
  renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

  def clean_renewal_date(self):
    data = self.cleaned_data['renewal_date']

    # Vérifier que la date ne se situe pas dans le passé.
    if data < datetime.date.today():
      raise ValidationError(_('Invalid date - renewal in past'))

      # Vérifier que la date tombe dans le bon intervalle (entre maintenant et dans 4 semaines).
    if data > datetime.date.today() + datetime.timedelta(weeks=4):
      raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

    # N'oubliez pas de toujours renvoyer les données nettoyées.
    return data
