from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


def redirect_to_orders_main_page(request):
    return HttpResponseRedirect(reverse("orders:list"))


def do_nothing(request, **kwargs):
    return render(request, "default.html")
