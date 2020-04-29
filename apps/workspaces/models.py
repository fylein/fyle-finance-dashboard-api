"""
Workspace Models
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Enterprise(models.Model):
    """
    Enterprise
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')
    id = models.AutoField(primary_key=True, serialize=False)
    name = models.TextField(blank=True, null=True, verbose_name='Enterprise name')
    users = models.ManyToManyField(User, help_text='User id mapping to enterprise table')


class Orgs(models.Model):
    """
    Orgs
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')
    id = models.AutoField(primary_key=True, serialize=False)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.deletion.PROTECT)
    refresh_token = models.TextField(blank=True, null=True, verbose_name='Refresh token')
    org_id = models.CharField(max_length=255, unique=True, verbose_name='org id')
    org_name = models.TextField(blank=True, null=True, verbose_name='Org name')


class Exports(models.Model):
    """
    Exports
    """
    created_at = models.DateTimeField(auto_now_add=True, help_text='created at time')
    updated_at = models.DateTimeField(auto_now=True, help_text='updated at time')
    id = models.AutoField(primary_key=True, serialize=False)
    enterprise = models.ForeignKey(Enterprise, on_delete=models.deletion.PROTECT)
    status = models.TextField(blank=True, null=True, verbose_name='Status')
    total_rows = models.IntegerField(verbose_name='No. of rows', default=0)
    gsheet_link = models.TextField(blank=True, null=True, verbose_name='Gsheet link')