import datetime

from django import forms
from dal import autocomplete
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from .models import BookInstance, Book, Author


def verify_4week_loan_period(date):
    if date < datetime.date.today():
        raise ValidationError(_('Invalid date - date in past'))

    if date > datetime.date.today() + datetime.timedelta(weeks=4):
        raise ValidationError(_('Invalid date - more than 4 weeks ahead'))

    return date


class RenewBookForm(forms.Form):
    """
    Form for renewing book.
    """
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        date = self.cleaned_data['renewal_date']
        if date is None:
            return date
        return verify_4week_loan_period(date)


class ChangeBookStatusForm(forms.ModelForm):

    def clean(self):
        cleaned_data = super(ChangeBookStatusForm, self).clean()
        status = cleaned_data['status']
        if status == 'o':
            if cleaned_data.get('borrower') is None:
                raise ValidationError(_('Missing required borrower.'))
            if cleaned_data.get('due_back') is None:
                raise ValidationError(_('Missing required due date.'))

        return cleaned_data

    def clean_due_back(self):
        date = self.cleaned_data['due_back']
        if date is None:
            return date
        return verify_4week_loan_period(date)

    class Meta:
        model = BookInstance
        fields = ['status', 'borrower', 'due_back']
        widgets = {
            'borrower': autocomplete.ModelSelect2(url='user_id-autocomplete')
        }


class BookForm(forms.ModelForm):

    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'author': autocomplete.ModelSelect2(url='author-autocomplete'),
            'genre': autocomplete.ModelSelect2Multiple(url='genre-autocomplete'),
        }
