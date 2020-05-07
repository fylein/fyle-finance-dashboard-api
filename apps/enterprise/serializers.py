"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Enterprise, Orgs, Exports


class EnterpriseSerializer(serializers.ModelSerializer):
    """
    Enterprise Serializer
    """
    class Meta:
        model = Enterprise
        fields = ['name', 'id']


class OrgsSerializer(serializers.ModelSerializer):
    """
   Organizations serializer
    """

    class Meta:
        model = Orgs
        fields = '__all__'


class ExportSerializer(serializers.ModelSerializer):
    """
    Exports serializer
    """

    class Meta:
        model = Exports
        fields = '__all__'
