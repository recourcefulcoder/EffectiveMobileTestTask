from django import forms
from django.utils.translation import gettext as _

from .models import Order


def item_form_data_creation(items):
    data = {
        "form-TOTAL_FORMS": len(items),
        "form-INITIAL_FORMS": len(items),
    }
    cnt = 0
    for key, value in items.items():
        data[f"form-{cnt}-name"] = key
        data[f"form-{cnt}-price"] = value
        cnt += 1
    return data


def dict_from_item_form_data(data):
    items = dict()
    i = 0
    for cnt in range(int(data["form-TOTAL_FORMS"])):
        while f"form-{i}-price" not in data.keys():
            i += 1
        items[data[f"form-{i}-name"]] = int(data[f"form-{i}-price"])
        i += 1
    return items


class OrderCreationForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ["total_price", "items"]


class ItemForm(forms.Form):
    name = forms.CharField(
        label=_("item name"),
        max_length=150,
        widget=forms.TextInput(attrs={"required": True}),
    )
    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={"required": True})
    )
