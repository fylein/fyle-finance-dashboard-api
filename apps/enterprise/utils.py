
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import gspread
from ..fyle.utils import FyleConnector
from fyle_finance_dashboard_api.utils import format_expenses, get_headers
from .models import Org, Export
from apps.users.models import User
from rest_framework.views import status
from rest_framework.response import Response
from .serializers import ExportSerializer
from django.conf import settings
import json

scope = [
            'https://www.googleapis.com/auth/analytics.readonly',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]


class GoogleSpreadSheet:
    def __init__(self):
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(settings.GSHEET_CREDS), scope)
        self.client = gspread.authorize(creds)
        self.service = discovery.build('sheets', 'v4', credentials=creds)
        self.range_ = 'A1:Z'
        self.SYNC_SUCCESSFUL = "Completed"
        self.SYNC_FAILED = "Failed"
        self.DEFAULT_SYNC_STATUS = "In progress"

    def create_sheet(self):
        sheet = self.client.create('Fyle-GDS')
        return sheet.id

    def share_sheet(self, sheet_id, email_id):
        sheet = self.client.open_by_key(sheet_id)
        sheet.share(email_id, perm_type='user', role='writer')

    def write_data(self, orgs, sheet_id):
        data_to_export, total_orgs = [get_headers()], len(orgs)
        for org in orgs.values():
            fyle_tpa_data = FyleConnector(org['refresh_token'])
            expenses = fyle_tpa_data.get_expenses()
            data_to_export += format_expenses(expenses)

        value_range_body = {
            'values': data_to_export
        }
        self.service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=self.range_).execute()
        request = self.service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=self.range_,
            valueInputOption='RAW',
            body=value_range_body)
        response = request.execute()
        rows = len(data_to_export)-1
        if response:
            return True, rows, total_orgs
        return False, 0, total_orgs


def write_gsheet(user, enterprise_id):

    gsheet_object = GoogleSpreadSheet()
    user = User.objects.get(user_id=user)
    try:
        export = Export.objects.get(enterprise_id=enterprise_id)
        export.status = gsheet_object.DEFAULT_SYNC_STATUS
        sheet_id = export.gsheet_link
        export.save()

    except Export.DoesNotExist:
        sheet_id = gsheet_object.create_sheet()
        export = Export(status=gsheet_object.DEFAULT_SYNC_STATUS, enterprise_id=enterprise_id, gsheet_link=sheet_id)
        export.save()

    org = Org.objects.filter(enterprise_id=enterprise_id).exclude(refresh_token__isnull=True)
    export = Export.objects.get(enterprise_id=enterprise_id)
    response, rows, total_orgs = gsheet_object.write_data(org, sheet_id)
    if response:
        response_status = status.HTTP_200_OK
        gsheet_object.share_sheet(sheet_id, user.email)
        export.status = gsheet_object.SYNC_SUCCESSFUL
    else:
        response_status = status.HTTP_400_BAD_REQUEST
        export.status = gsheet_object.SYNC_FAILED

    export.total_rows = rows
    export.gsheet_link = sheet_id
    export.total_orgs = total_orgs
    export.save()
    return Response(
        status=response_status
    )


def share_gsheet(user_id, enterprise_id):

    export = Export.objects.filter(enterprise_id=enterprise_id).first()
    export_data = ExportSerializer(export).data
    if export:
        user_email = User.objects.get(user_id=user_id).email
        GoogleSpreadSheet().share_sheet(export_data['gsheet_link'], user_email)
