from django.http import HttpResponse, HttpRequest
from django.shortcuts import render

# Create your views here.

def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")