"""
Registering models in Django Admin
"""
from django.contrib import admin
from .models import Enterprise


admin.site.register(Enterprise)
