from django import forms
from django.utils.translation import gettext as _


class SearchForm(forms.Form):
    query = forms.CharField(
        max_length=10,
        help_text=_("Search orders..."),
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
