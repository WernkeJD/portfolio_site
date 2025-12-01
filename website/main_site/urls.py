from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('contact_form', views.contact_form, name="contact_form"),
    path('new_home', views.new_home, name='new_home')
]