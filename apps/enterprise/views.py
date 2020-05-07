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

User = get_user_model()
auth_utils = AuthUtils()


class EnterpriseView(generics.ListCreateAPIView):
    """
    Fyle Finance Export
    """

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
            data= {
                'messages': "Unable to create Enterprise",
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class OrgView(generics.ListCreateAPIView):

    def post(self, request, **kwargs):

        fields = ['org_name', 'org_id', 'enterprise_id']
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

    def get(self, request, **kwargs):
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


class ExportView(generics.ListCreateAPIView):

    def post(self, request,  **kwargs):

        enterprise_id = request.data['id']
        default_status = "Sync pending"
        gsheet_object = gsheet.GoogleSpreadSheet()
        try:
            export = Exports.objects.get(enterprise_id=enterprise_id)
            export.status = default_status
            sheet_id = export.gsheet_link
            export.save()

        except Exports.DoesNotExist:
            user = User.objects.get(user_id=request.user)
            sheet_id = gsheet_object.create_sheet(user.email)
            export = Exports(status=default_status, enterprise_id=enterprise_id, gsheet_link=sheet_id)
            export.save()

        orgs = Orgs.objects.filter(enterprise_id=enterprise_id)
        export = Exports.objects.get(enterprise_id=enterprise_id)
        response, rows = gsheet_object.write_data(orgs, sheet_id)
        if response:
            export.status = "Sync completed"
            response_status = status.HTTP_200_OK
        else:
            export.status = "Sync Error"
            response_status = status.HTTP_400_BAD_REQUEST
        export.total_rows = rows
        export.gsheet_link = sheet_id
        export.save()
        return Response(
            data={
                'message': 'Sync completed',
                'org': len(orgs),
                'sheet_id': sheet_id,
            },
            status=response_status
        )

    def get(self, request, **kwargs):
        """
        Get Exports by Id
        """
        try:
            export = Exports.objects.get(enterprise_id=kwargs['enterprise_id'])
            return Response(
                data=ExportSerializer(export).data,
                status=status.HTTP_200_OK
            )
        except Exports.DoesNotExis:
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
        except Enterprise.DoesNotExis:
            try:
                orgs = Orgs.objects.get(org_id=request.data['org_id'])
                enterprise = Enterprise.objects.get(id=orgs.enterprise_id)
                enterprise.users.add(User.objects.get(user_id=request.user))
                enterprise = Enterprise.objects.get(users__in=[request.user])
                data = EnterpriseSerializer(enterprise).data
            except Exception as e:
                response_status = status.HTTP_401_UNAUTHORIZED
                data = {}
        return Response(
            status=response_status,
            data=data
        )


class ConnectFyleView(viewsets.ViewSet):
    """
    Fyle Connect Oauth View
    """
    def post(self, request, **kwargs):
        """
        Post of Adding Fyle org refresh token
        """
        try:
            authorization_code = request.data.get('code')

            refresh_token = auth_utils.generate_fyle_refresh_token(authorization_code)['refresh_token']
            fyle_user = auth_utils.get_fyle_user(refresh_token)
            org_id = fyle_user['org_id']

            org_credential, _ = Orgs.objects.update_or_create(
                org_id=org_id,
                defaults={
                    'refresh_token': refresh_token,
                }
            )

            return Response(
                data=OrgsSerializer(org_credential).data,
                status=status.HTTP_200_OK
            )
        except fyle_exc.UnauthorizedClientError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except fyle_exc.NotFoundClientError:
            return Response(
                {
                    'message': 'Fyle Application not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        except fyle_exc.WrongParamsError:
            return Response(
                {
                    'message': 'Some of the parameters are wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except fyle_exc.InternalServerError:
            return Response(
                {
                    'message': 'Wrong/Expired Authorization code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
