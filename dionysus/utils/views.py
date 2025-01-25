from django.http import HttpResponseRedirect
from django.urls import reverse


def redirect_to_orders_main_page(request):
    return HttpResponseRedirect(reverse('orders:list'))
