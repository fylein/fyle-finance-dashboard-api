import json
from django.conf import settings

import gspread
from fyle_rest_auth.models import AuthToken
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from rest_framework.views import status

from apps.fyle.utils import FyleConnector
from apps.users.models import User

from fyle_finance_dashboard_api.utils import format_expenses, get_headers

from .models import Org, Export


scope = [
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]

SYNC_SUCCESSFUL = 'COMPLETED'
SYNC_FAILED = 'FAILED'
DEFAULT_SYNC_STATUS = 'IN_PROGRESS'
        

class GoogleSpreadSheet:
    def __init__(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(
            json.loads(settings.GOOGLE_SHEETS_CREDENTIALS), scope)
        self.client = gspread.authorize(credentials)
        self.service = discovery.build('sheets', 'v4', credentials=credentials)
        self.range = 'A1:Z'

    def create_sheet(self):
        sheet = self.client.create('Fyle-GDS')
        return sheet.id

    def share_sheet(self, sheet_id, email_id):
        sheet = self.client.open_by_key(sheet_id)
        sheet.share(email_id, perm_type='user', role='writer')

    def write_data(self, orgs, sheet_id):
        data_to_export, total_orgs = [get_headers()], len(orgs)

        for org in orgs.values():
            fyle_connector = FyleConnector(org['refresh_token'])
            expenses = fyle_connector.get_expenses()
            data_to_export.extend(format_expenses(expenses))

        data = {
            'values': data_to_export
        }
        self.service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=self.range).execute()
        request = self.service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=self.range,
            valueInputOption='RAW',
            body=data
        )
        response = request.execute()
        rows = len(data_to_export) - 1
        if response:
            return True, rows, total_orgs
        return False, 0, total_orgs


def schedule_export(enterprise_id, user):
    google_sheet_object = GoogleSpreadSheet()

    export = Export.objects.filter(enterprise_id=enterprise_id).first()

    sheet_id = export.google_sheets_link if export else google_sheet_object.create_sheet()

    export, _ = Export.objects.update_or_create(
        enterprise_id=enterprise_id,
        defaults={
            'status': DEFAULT_SYNC_STATUS,
            'google_sheets_link': sheet_id,
        }
    )

    fyle_credentials = AuthToken.objects.get(user__user_id=user)

    fyle_connector = FyleConnector(fyle_credentials.refresh_token)

    created_job = fyle_connector.trigger_job(
        callback_url='{0}{1}'.format(settings.API_URL, '/enterprises/{0}/exports/'.format(enterprise_id)),
        callback_method='POST', object_id=export.id, payload={},
        job_description='Running export for Enterprise id: {0}'.format(
            enterprise_id
        ),
        org_user_id=fyle_connector.get_employee_profile()['id']
    )

    export.job_id = created_job['id']
    export.save()
    return created_job


def write_google_sheet(user, enterprise_id):
    google_sheet_object = GoogleSpreadSheet()
    user = User.objects.get(user_id=user)

    orgs = Org.objects.filter(enterprise_id=enterprise_id).exclude(refresh_token__isnull=True)

    export = Export.objects.get(enterprise_id=enterprise_id)

    response, rows, total_orgs = google_sheet_object.write_data(orgs, export.google_sheets_link)
    if response:
        google_sheet_object.share_sheet(export.google_sheets_link, user.email)
        export.status = 'COMPLETE'
    else:
        export.status = 'FAILED'

    export.total_rows = rows
    export.total_orgs = total_orgs
    export.save(update_fields=['status', 'total_rows', 'total_orgs'])

    return export


def share_google_sheet(user_id, enterprise_id):
    export = Export.objects.filter(enterprise_id=enterprise_id).first()
    if export:
        user_email = User.objects.get(user_id=user_id).email
        GoogleSpreadSheet().share_sheet(export.google_sheets_link, user_email)
