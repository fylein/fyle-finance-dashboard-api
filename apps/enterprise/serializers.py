"""
Workspace Serializers
"""
from rest_framework import serializers

from .models import Enterprise, Orgs, Exports


class EnterpriseSerializer(serializers.ModelSerializer):
    """
    Workspace Schedule Serializer
    """
    class Meta:
        model = Enterprise
        fields = ['name', 'id']


class OrgsSerializer(serializers.ModelSerializer):
    """
    Workspace settings serializer
    """

    class Meta:
        model = Orgs
        fields = '__all__'


class ExportSerializer(serializers.ModelSerializer):
    """
    Workspace settings serializer
    """

    class Meta:
        model = Exports
        fields = '__all__'
