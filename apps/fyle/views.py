from fylesdk import exceptions
from rest_framework import generics, status
from rest_framework.response import Response

from apps.enterprise.models import Org
from apps.enterprise.serializers import OrgsSerializer
from apps.enterprise.views import auth_utils


class ConnectFyleView(generics.CreateAPIView):
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
            user_email = fyle_user['employee_email']
            Org.objects.get(org_id=org_id, enterprise_id=kwargs['enterprise_id'])
            org_credential, _ = Org.objects.update_or_create(
                org_id=org_id,
                defaults={
                    'refresh_token': refresh_token,
                    'added_by': user_email
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
        except exceptions.UnauthorizedClientError:
            return Response(
                {
                    'message': 'Invalid Authorization Code'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except exceptions.NotFoundClientError:
            return Response(
                {
                    'message': 'Fyle Application not found'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except exceptions.WrongParamsError:
            return Response(
                {
                    'message': 'Some of the parameters are wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except exceptions.InternalServerError:
            return Response(
                {
                    'message': 'Wrong/Expired Authorization code'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
