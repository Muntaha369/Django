from django.shortcuts import render
from django.http import HttpResponse

def hello_world_view(request):
    return HttpResponse('Hello world') #type:ignore
# Create your views here.
def hello_name(request, name:str): #This takes name from the dynamic url route like (helloname/{name})
    return HttpResponse(f'Hello {name}') #type:ignore 