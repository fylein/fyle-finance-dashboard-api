import json

from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from fyle_rest_auth.utils import AuthUtils

from .models import Enterprise, Orgs, Exports
from ..users.models import User
from .serializers import ExportSerializer, EnterpriseSerializer, OrgsSerializer
from ..exports import gsheet
from ..fyle.utils import FyleConnector
from fyle_finance_dashboard_api.utils import format_tpa, headers

User = get_user_model()
auth_utils = AuthUtils()


class EnterpriseView(viewsets.ViewSet):
    """
    Fyle Finance Export
    """

    def post_enterprise(self, request, **kwargs):

        enterprise = Enterprise(name=request.data['name'])
        enterprise.save()
        if enterprise:
            return Response(
                data={
                    'name': request.data['name'],
                    'id': enterprise.id
                },
                status=status.HTTP_200_OK
            )
        return Response(
            data= {
                'messages': "Unable to create Enterprise",
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class OrgView(viewsets.ViewSet):

    def post_org(self, request, **kwargs):

        fields = ['org_name', 'org_id', 'enterprise_id', 'refresh_token']
        for field in fields:
            if field not in request.data:
                return Response(
                    data= {
                        'messages': "{} Field is missing".format(field),
                    },
                    status= status.HTTP_400_BAD_REQUEST
                )
        orgs = Orgs(org_name=request.data['org_name'], org_id=request.data['org_id'], enterprise_id=request.data['enterprise_id'], refresh_token=request.data['refresh_token'])
        orgs.save()
        if orgs:
            return Response(
                data={
                    'name': request.data['org_name'],
                    'id': request.data['enterprise_id']
                },
                status=status.HTTP_200_OK
            )
        return Response(
            data = {
                'messages': "Unable to add org"
            },
            status= status.HTTP_400_BAD_REQUEST
        )

    def get_orgs(self, request, **kwargs):
        """
        Get Orgs by enterprise id
        """
        orgs = Orgs.objects.filter(enterprise_id=kwargs['enterprise_id'])
        if orgs:
            return Response(
                data=OrgsSerializer(orgs, many=True).data if orgs else [],
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                data={
                    'message': 'Enterprise with this id does not exist'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ExportView(viewsets.ViewSet):

    def post_export(self, request):

        enterprise_id = request.data['id']
        data_to_export = [headers()]
        default_status = "Sync is in progress"
        gsheet_object = gsheet.GoogleSpreadSheet()
        try:
            export = Exports.objects.get(enterprise_id=enterprise_id)
            export.status = default_status
            sheet_id = export.gsheet_link
            export.save()
        except Exception as e:
            export = Exports(status=default_status, enterprise_id=enterprise_id)
            export.save()
            user = User.objects.get(user_id=request.user)
            sheet_id = gsheet_object.create_sheet(user.email)

        try:
            orgs = Orgs.objects.filter(enterprise_id=enterprise_id)
            for org in orgs.values():
                fyle_tpa_data = FyleConnector(org['refresh_token'])
                data_to_export += format_tpa(fyle_tpa_data.get_fyle_tpa())
            gsheet_object.write_data(data_to_export, sheet_id)
            export = Exports.objects.get(enterprise_id=enterprise_id)
            export.status = "Sync completed"
            export.total_rows = len(data_to_export)-1
            export.gsheet_link = sheet_id
            export.save()
            return Response(
                data={
                    'message': 'Sync completed',
                    'data': len(orgs),
                    'sheet_id': sheet_id,
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            print(e)
            return Response(
                data={
                    'message': 'No exports found'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_export(self, request, **kwargs):
        """
        Get Exports by Id
        """
        try:
            export = Exports.objects.get(enterprise_id=kwargs['enterprise_id'])
            return Response(
                data=ExportSerializer(export).data,
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                data={
                    'message': 'Exports not Available'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAccountMapping(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Get User Details
        """

        response_status = status.HTTP_200_OK
        try:
            enterprise = Enterprise.objects.get(users__in=[request.user])
            data = EnterpriseSerializer(enterprise).data
        except Exception as e:
            try:
                orgs = Orgs.objects.get(org_id=request.data['org_id'])
                enterprise = Enterprise.objects.get(id=orgs.enterprise_id)
                enterprise.users.add(User.objects.get(user_id=request.user))
                enterprise = Enterprise.objects.get(users__in=[request.user])
                data = EnterpriseSerializer(enterprise).data
            except Exception as e:
                response_status = status.HTTP_400_BAD_REQUEST
                data = {}
        return Response(
            status=response_status,
            data=data
        )
