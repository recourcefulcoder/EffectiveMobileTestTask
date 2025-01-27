from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import formset_factory
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .forms import (
    ItemForm,
    OrderCreationForm,
    dict_from_item_form_data,
    item_form_data_creation,
)
from .models import Order


def do_nothing(request, **kwargs):
    return render(request, "default.html")


def delete_order(request, pk):
    try:
        order = Order.objects.get(pk=pk)
        order.delete()
    except Order.DoesNotExist:
        messages.error(request, _("Order with provided ID not found"))
        return redirect("orders:list")
    messages.success(request, _("Order successfully deleted!"))
    return redirect("orders:list")


class OrderList(ListView):
    template_name = "orders/list.html"
    model = Order
    context_object_name = "orders_list"

    def get_queryset(self):
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


class OrderFormProcessMixin:
    def get_items_formset(self, items=None):
        if items is None:
            return formset_factory(ItemForm, min_num=1, validate_min=True)(
                error_messages={
                    "too_few_forms": _("Add at least one item for order")
                }
            )

        formset = formset_factory(ItemForm, min_num=1, validate_min=True)(
            item_form_data_creation(items),
            error_messages={
                "too_few_forms": _("Add at least one item for order")
            },
        )
        return formset

    def process_post(self, request, success_message, force_update=False):
        data = request.POST
        # print('processing_data', type(data), data)

        items = dict_from_item_form_data(data)

        formset = self.get_items_formset(items=items)
        if not formset.is_valid():
            messages.error(
                request, _("Invalid items data - maybe you forgot to add any?")
            )
            raise ValidationError(_("Formset invalid"))

        order_data = {
            "table_number": data["table_number"],
            "status": data["status"],
            "items": items,
        }

        try:
            if force_update:
                order_data["pk"] = int(request.resolver_match.kwargs.get("pk"))

            # print(order_data)
            Order(**order_data).save(force_update=force_update)
            messages.success(request, success_message)
        except ValidationError as e:
            messages.error(request, e)


class OrderProcessView(OrderFormProcessMixin, FormView):
    model = Order
    form_class = OrderCreationForm
    template_name = "orders/order_detail.html"

    def get_context_data(self, submit_message=None, items=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["formset"] = self.get_items_formset(items)
        if submit_message is not None:
            context["submit_message"] = submit_message
        return context


class AddOrder(OrderProcessView):
    def get_context_data(self, submit_message=None, **kwargs):
        return super().get_context_data(submit_message=_("Add order"))

    def post(self, request, *args, **kwargs):
        try:
            self.process_post(request, _("New order successfully added!"))
        except ValidationError:
            return redirect(
                "orders:add", request.resolver_match.kwargs.get("pk")
            )
        return self.get(request)


class EditOrder(OrderProcessView):
    def get_context_data(self, **kwargs):
        instance = Order.objects.get(pk=kwargs["pk"])
        context = super().get_context_data(
            items=instance.items,
            submit_message=_("Change order"),
            **kwargs,
        )
        context["form"] = self.get_form_class()(instance=instance)
        return context

    def post(self, request, *args, **kwargs):
        try:
            self.process_post(
                request, _("Order successfully updated"), force_update=True
            )
        except ValidationError:
            return redirect(
                "orders:edit", request.resolver_match.kwargs.get("pk")
            )
        return redirect("orders:list")

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
