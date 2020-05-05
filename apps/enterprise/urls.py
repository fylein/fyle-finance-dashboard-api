"""fyle_qbo URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include

from .views import EnterpriseView, UserAccountMapping, ExportView, OrgView

urlpatterns = [
    path('orgs/<int:enterprise_id>', OrgView.as_view({'get': 'get_orgs'})),
    path('exports/<int:enterprise_id>', ExportView.as_view({'get': 'get_export'})),
    path('exports/', ExportView.as_view({'post': 'post_export'})),
    path('user/map_user/', UserAccountMapping.as_view()),
    path('enterprise/', EnterpriseView.as_view({'post': 'post_enterprise'})),
    path('orgs/', OrgView.as_view({'post': 'post_org'}))
]
