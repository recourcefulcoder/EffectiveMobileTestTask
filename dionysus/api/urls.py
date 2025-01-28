from django.urls import path

from utils.views import do_nothing

app_name = "api"
urlpatterns = [path("delete/<int:pk>/", view=do_nothing, name="delete")]
