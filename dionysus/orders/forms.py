from django import forms
from django.utils.translation import gettext as _

from .models import Order


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["total_price", "items"]


class ItemForm(forms.Form):
    name = forms.CharField(label=_("item name"), max_length=150)
    price = forms.IntegerField()


# class ItemsWidget(Widget):
#     pass
#
#     class Media:
#         css = {
#             'all': ['/css/bootstrap.min.css'],
#         }
#         js = ['/js/bootstrap.min.js']
