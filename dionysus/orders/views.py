from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import formset_factory
from django.shortcuts import render
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import ItemForm, OrderCreationForm
from .models import Order


def do_nothing(request, **kwargs):
    return render(request, "default.html")


class OrderList(ListView):
    template_name = "orders/list.html"
    model = Order
    context_object_name = "orders_list"

    def get_queryset(self):
        # print(Order.objects.all().order_by('status'))
        return Order.objects.all().order_by("status")


class IncomeView(TemplateView):
    template_name = "orders/income.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["income"] = Order.objects.filter(status="paid").aggregate(
            Sum("total_price")
        )["total_price__sum"]
        if context["income"] is None:
            context["income"] = 0
        return context


class AddOrder(FormView):
    model = Order
    form_class = OrderCreationForm
    template_name = "orders/add.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = formset_factory(ItemForm, extra=1)
        return context

    def post(self, request, *args, **kwargs):
        data = request.POST
        new_order = Order(
            table_number=data["table_number"], status=data["status"]
        )
        items = dict()
        for i in range(int(data["form-TOTAL_FORMS"])):
            if data[f"form-{i}-price"]:
                items[data[f"form-{i}-name"]] = int(data[f"form-{i}-price"])
        new_order.items = items
        try:
            new_order.full_clean()
            new_order.save()
            messages.success(request, _("New order successfully added!"))
        except ValidationError as e:
            messages.error(request, e)
        return self.get(request, "orders/add.html")
