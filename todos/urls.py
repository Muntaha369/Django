from django.urls import path
from . import views

urlpatterns = [
    path('hello', views.hello_world_view, name = "hello world"),
    path('helloname/<str:name>', views.hello_name, name = "hello world")
]