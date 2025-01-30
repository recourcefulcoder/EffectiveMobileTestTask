from typing import Dict, Final, Optional, Union

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.forms import formset_factory
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from utils.functions import normalize

from .forms import (
    ItemForm,
    OrderCreationForm,
    dict_from_item_form_data,
    item_form_data_creation,
)
from .models import Order, STATUS_CHOICES

ORDER_LIST_CONTEXT_NAME: Final = "orders_list"


def delete_order(request, pk):
    try:
        Order.objects.filter(pk=pk).delete()
    except Order.DoesNotExist:
        messages.error(request, _("Order with provided ID not found"))
        return redirect("orders:list")
    messages.success(request, _("Order successfully deleted!"))
    return redirect("orders:list")


class OrderList(ListView):
    template_name = "orders/list.html"
    model = Order
    context_object_name = ORDER_LIST_CONTEXT_NAME
    allow_empty = True

    def get_queryset(self):
        params = self.request.GET.dict()
        if not params or not params["q"]:
            return Order.objects.all()
        query = normalize(params["q"])
        # print(f"QUERY: |{query}|")

        if query.isdigit():
            try:
                return Order.objects.filter(pk=int(query))
            except Order.DoesNotExist:
                return None

        db_query = []
        for db, verbose in STATUS_CHOICES:
            if query in verbose:
                db_query.append(db)

        return Order.objects.filter(status__in=db_query)


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
    def get_items_formset(
        self, items: Optional[Dict[str, Union[int, str]]] = None
    ):
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

    def process_post(
        self, request, success_message: str, force_update: bool = False
    ) -> bool:
        process_success: bool = True
        data = request.POST

        formset = formset_factory(ItemForm)(data)
        for form in formset:
            if not form.is_valid():
                messages.error(request, "Empty order item passed")
                return False

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

            order = Order(**order_data)
            order.full_clean(exclude={"id"})
            order.save(force_update=force_update)
            messages.success(request, success_message)
        except ValidationError as e:
            process_success = False
            if hasattr(e, "message_dict"):
                for error in e.message_dict:
                    messages.error(request, e.message_dict[error][0])
            else:
                messages.error(request, e)
        return process_success


class OrderProcessView(OrderFormProcessMixin, FormView):
    model = Order
    form_class = OrderCreationForm
    template_name = "orders/order_detail.html"

    def get_context_data(
        self,
        submit_message: Optional[str] = None,
        items: Optional[Dict[str, Union[str, int]]] = None,
        **kwargs,
    ):
        context = super().get_context_data(**kwargs)
        context["formset"] = self.get_items_formset(items)
        if submit_message is not None:
            context["submit_message"] = submit_message
        return context


class AddOrder(OrderProcessView):
    def get_context_data(self, submit_message: Optional[str] = None, **kwargs):
        return super().get_context_data(submit_message=_("Add order"))

    def post(self, request, *args, **kwargs):
        success: bool = self.process_post(
            request, _("New order successfully added!")
        )
        if success:
            return self.get(request)
        return redirect("orders:add")


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
        success: bool = self.process_post(
            request, _("Order successfully updated"), force_update=True
        )
        if success:
            return redirect("orders:list")
        return redirect("orders:edit", request.resolver_match.kwargs.get("pk"))

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)
