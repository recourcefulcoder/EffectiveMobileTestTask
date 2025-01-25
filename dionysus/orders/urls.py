from django.urls import path

from . import views

app_name = 'orders'
urlpatterns = [
    path('', view=views.OrderList.as_view(), name='list'),
    path('add/', view=views.do_nothing, name='add'),
    path('edit/<int:pk>/', view=views.do_nothing, name='edit'),
    path('delete/<int:pk>/', view=views.do_nothing, name='delete'),
]
