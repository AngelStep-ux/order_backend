from django.shortcuts import render
from django.http import HttpResponse

def intial_page(request):
    return HttpResponse('Welcome to the web service for ordering goods!')


# Create your views here.
