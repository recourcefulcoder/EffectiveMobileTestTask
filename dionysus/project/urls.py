from django.contrib import admin
from django.urls import include, path

from utils import views

urlpatterns = [
    path('', view=views.redirect_to_orders_main_page, name='homepage'),
    path('admin/', admin.site.urls),
    path('orders/', include('orders.urls')),
]
