from django.shortcuts import render
from django.views.generic.list import ListView

from .models import Order


def do_nothing(request, **kwargs):
    return render(request, 'default.html')


class OrderList(ListView):
    template_name = 'orders/list.html'
    model = Order
    context_object_name = 'orders_list'

    def get_queryset(self):
        print(Order.objects.all().order_by('status'))
        return Order.objects.all().order_by('status')
