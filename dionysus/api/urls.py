from django.urls import path

from rest_framework.urlpatterns import format_suffix_patterns

from .views import OrderDetail, OrderList

app_name = "api"
urlpatterns = [
    path("", view=OrderList.as_view(), name="list"),
    path("<int:pk>/", view=OrderDetail.as_view(), name="delete"),
]

urlpatterns = format_suffix_patterns(urlpatterns)
