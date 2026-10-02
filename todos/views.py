from django.shortcuts import render
from django.http import HttpResponse

def hello_world_view(request):
    return HttpResponse('Hello world') #type:ignore
# Create your views here.
