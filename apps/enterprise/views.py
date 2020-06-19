from django.contrib.auth import get_user_model

from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.permissions import IsAuthenticated

from fyle_rest_auth.utils import AuthUtils

from fyle_finance_dashboard_api.utils import assert_valid

from .models import Enterprise, Org, Export
from .serializers import ExportSerializer, EnterpriseSerializer, OrgsSerializer
from .utils import write_google_sheet, share_google_sheet, schedule_export

User = get_user_model()
auth_utils = AuthUtils()


class EnterpriseView(generics.ListCreateAPIView):
    """
    Fyle Finance Export
    """
    permission_classes = []
    authentication_classes = []

    def post(self, request, **kwargs):

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
            data={
                'messages': "Unable to create Enterprise",
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class OrgView(generics.ListCreateAPIView):

    serializer_class = OrgsSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, **kwargs):
        org_name = request.data['org_name'] or None
        org_id = request.data['org_id'] or None
        enterprise_id = request.data['enterprise_id'] or None

        assert_valid(org_name is not None, 'Org name not found in payload')
        assert_valid(org_id is not None, 'Org id not found in payload')
        assert_valid(enterprise_id is not None, 'Enterprise id not found in payload')

        org, _ = Org.objects.update_or_create(
            org_name=org_name,
            org_id=org_id,
            enterprise_id=enterprise_id
        )

        return Response(
            data=OrgsSerializer(org).data,
            status=status.HTTP_200_OK
        )

    def get_queryset(self):
        return Org.objects.filter(enterprise_id=self.kwargs['enterprise_id'])


class ExportScheduleView(generics.CreateAPIView):

    def post(self, request,  **kwargs):
        enterprise_id = kwargs['enterprise_id']

        return Response(
            data=schedule_export(enterprise_id, request.user),
            status=status.HTTP_200_OK
        )


class ExportView(generics.ListCreateAPIView):

    def post(self, request,  **kwargs):

        enterprise_id = kwargs['enterprise_id']
        write_google_sheet(request.user, enterprise_id)

        return Response(
            data={},
            status=status.HTTP_200_OK
        )

    def get(self, request, **kwargs):
        """
        Get Export by Id
        """
        try:
            export = Export.objects.get(enterprise_id=kwargs['enterprise_id'])
            return Response(
                data=ExportSerializer(export).data,
                status=status.HTTP_200_OK
            )
        except Export.DoesNotExist:
            return Response(
                data={
                    'status': 'Not synced yet'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAccountMapping(generics.CreateAPIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Get User Details
        """
        response_status = status.HTTP_200_OK
        enterprise = Enterprise.objects.filter(users__in=[request.user]).first()
        data = EnterpriseSerializer(enterprise).data
        if not enterprise:
            try:
                org = Org.objects.get(org_id=request.data['org_id'])
                enterprise = Enterprise.objects.get(id=org.enterprise_id)
                enterprise.users.add(User.objects.get(user_id=request.user))
                enterprise = Enterprise.objects.get(users__in=[request.user])
                data = EnterpriseSerializer(enterprise).data
            except Org.DoesNotExist:
                return Response(
                    {
                        'message': "Org Doesn't Exist"
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        share_google_sheet(request.user, data['id'])
        return Response(
            status=response_status,
            data=data
        )
