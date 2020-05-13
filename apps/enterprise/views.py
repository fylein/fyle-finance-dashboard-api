from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .permissions import EnterprisePermissions
from fyle_rest_auth.utils import AuthUtils
from fylesdk import exceptions as fyle_exc

from .models import Enterprise, Org, Export
from apps.users.models import User
from .serializers import ExportSerializer, EnterpriseSerializer, OrgsSerializer
from .utils import write_gsheet

User = get_user_model()
auth_utils = AuthUtils()


class EnterpriseView(generics.ListCreateAPIView):
    """
    Fyle Finance Export
    """
    permission_classes = []

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

    serializer_class = OrgsSerializer

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
        org = Org(org_name=request.data['org_name'], org_id=request.data['org_id'], enterprise_id=request.data['enterprise_id'])
        org.save()
        if org:
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

    def get_queryset(self):
        return Org.objects.filter(enterprise_id=self.kwargs['enterprise_id'])


class ExportView(generics.ListCreateAPIView):

    def post(self, request,  **kwargs):

        enterprise_id = kwargs['enterprise_id']
        return write_gsheet(request.user, enterprise_id)

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
        except Enterprise.DoesNotExist:
            try:
                org = Org.objects.get(org_id=request.data['org_id'])
                enterprise = Enterprise.objects.get(id=org.enterprise_id)
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
            Org.objects.get(org_id=org_id, pk=kwargs['enterprise_id'])
            org_credential, _ = Org.objects.update_or_create(
                org_id=org_id,
                defaults={
                    'refresh_token': refresh_token,
                }
            )

            return Response(
                data=OrgsSerializer(org_credential).data,
                status=status.HTTP_200_OK
            )
        except Org.DoesNotExist:
            return Response(
                {
                    'message': "This org doesn't exist in this enterprise"
                },
                status=status.HTTP_404_NOT_FOUND
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
