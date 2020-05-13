"""
Enterprise Serializers
"""
from rest_framework import serializers

from .models import Enterprise, Org, Export


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
        model = Org
        fields = '__all__'


class ExportSerializer(serializers.ModelSerializer):
    """
    Exports serializer
    """

    class Meta:
        model = Export
        fields = '__all__'
