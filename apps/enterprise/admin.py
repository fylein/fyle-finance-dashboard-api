"""
Registering models in Django Admin
"""
from django.contrib import admin
from .models import Enterprise, Org


admin.site.register(Enterprise)
admin.site.register(Org)
