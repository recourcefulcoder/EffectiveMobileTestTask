from django.urls import path

from . import views

app_name = "orders"
urlpatterns = [
    path("", view=views.OrderList.as_view(), name="list"),
    path("add/", view=views.AddOrder.as_view(), name="add"),
    path("edit/<int:pk>/", view=views.EditOrder.as_view(), name="edit"),
    path("delete/<int:pk>/", view=views.delete_order, name="delete"),
    path("income/", view=views.IncomeView.as_view(), name="income_total"),
]
