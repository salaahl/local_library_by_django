from django.forms import ModelForm
from catalog.models import User, Book, Author, BookInstance, Genre
from django.core.exceptions import ValidationError
from django import forms
from django.utils.translation import gettext as _
import re
import datetime


class UserModelForm(ModelForm):
  
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'groups']


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


# Facon alternative (et plus modulaire) de déclarer un formulaire
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
            'imprint': ('Date d\'impression'),
            'due_back': ('Date de retour'),
            'status': ('Statut'),
            'book': ('Livre')
        }
        help_texts = {'status': ('Disponibilité du livre')}


class RenewBookForm(forms.Form):
    # Champ de date avec une valeur initiale
    renewal_date = forms.DateField(
        label=_("Renouveler jusqu'au "),
        initial=datetime.date.today() + datetime.timedelta(weeks=3),
        help_text=_("Ajoutez entre un et 28 jours (trois semaines par défaut)."),
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'min': (datetime.date.today() + datetime.timedelta(days=1)).isoformat(),
                'max': (datetime.date.today() + datetime.timedelta(weeks=4)).isoformat(),
            }
        )
    )

    # Méthode de validation personnalisée
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Vérifier que la date ne se situe pas dans le passé
        if data <= datetime.date.today():
            raise ValidationError(_('Erreur. Ajoutez au minimum un jour.'))

        # Vérifier que la date est dans un intervalle de 4 semaines maximum
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Erreur. Le renouvellement ne doit pas dépasser quatre semaines.'))

        # Toujours renvoyer les données nettoyées
        return data
