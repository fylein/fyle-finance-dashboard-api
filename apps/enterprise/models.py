"""
Enterprise Models
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Enterprise(models.Model):
    """
    Enterprise
    """
    id = models.AutoField(primary_key=True)
    name = models.TextField(blank=True, null=True, verbose_name='Enterprise name')
    users = models.ManyToManyField(User, help_text='User id mapping to enterprise table')
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')


class Org(models.Model):
    """
    Orgs
    """
    id = models.AutoField(primary_key=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    refresh_token = models.TextField(blank=True, null=True, verbose_name='Refresh token')
    org_id = models.CharField(max_length=255, unique=True, verbose_name='org id')
    org_name = models.TextField(blank=True, null=True, verbose_name='Org name')
    added_by = models.TextField(blank=True, null=True, verbose_name='Added by')
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')


class Export(models.Model):
    """
    Exports
    """
    id = models.AutoField(primary_key=True)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.PROTECT)
    status = models.TextField(blank=True, null=True, verbose_name='Status')
    total_rows = models.IntegerField(verbose_name='No. of rows', default=0)
    total_orgs = models.IntegerField(verbose_name='No. of orgs', default=0)
    job_id = models.CharField(max_length=255, help_text='Fyle job id')
    google_sheets_link = models.TextField(blank=True, null=True, verbose_name='Google sheets link')
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')
