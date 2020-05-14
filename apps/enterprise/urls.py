"""fyle_financial_dashboard_api URL Configuration

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

from .views import EnterpriseView, UserAccountMapping, ExportView, OrgView, ConnectFyleView

urlpatterns = [
    path('<int:enterprise_id>/orgs/', OrgView.as_view()),
    path('<int:enterprise_id>/exports/', ExportView.as_view()),
    path('add_user/', UserAccountMapping.as_view()),
    path('', EnterpriseView.as_view()),
    path('<int:enterprise_id>/connect_fyle/authorization_code/', ConnectFyleView.as_view({'post': 'post'}))
]