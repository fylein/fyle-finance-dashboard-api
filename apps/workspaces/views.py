import json

from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from fyle_rest_auth.utils import AuthUtils

from .models import Enterprise, Orgs, Exports

from .serializers import ExportSerializer, EnterpriseSerializer, OrgsSerializer
from ..exports import gsheet, fyle

User = get_user_model()
auth_utils = AuthUtils()


class WorkspaceView(viewsets.ViewSet):
    """
    Fyle Finance Export
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        enterprise_id = request.data['id']
        tpa_data_format = fyle.FormatData()
        data_to_export = [tpa_data_format.headers()]

        try:
            orgs = Orgs.objects.filter(enterprise_id=enterprise_id)
            for org in orgs.values():
                fyle_tpa_data = fyle.FyleTpaData(org['refresh_token'])
                data_to_export += tpa_data_format.format(fyle_tpa_data.fyle_tpa())

        except Exception as e:
            return Response(
                data={
                    'message': 'Exports not Available'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_orgs(self, request, **kwargs):
        """
        Get Workspace by id
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

    def get_exports(self, request, **kwargs):
        """
        Get Workspace by id
        """
        try:
            orgs = Exports.objects.get(enterprise_id=kwargs['enterprise_id'])
            return Response(
                data=ExportSerializer(orgs, many=True).data if orgs else [],
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
