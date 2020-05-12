from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import gspread
from ..fyle.utils import FyleConnector
from fyle_finance_dashboard_api.utils import format_expenses, get_headers
scope = [
            'https://www.googleapis.com/auth/analytics.readonly',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]


class GoogleSpreadSheet:
    def __init__(self):
        creds = ServiceAccountCredentials.from_json_keyfile_name('fyle_finance_dashboard_api/client_secret.json', scope)
        self.client = gspread.authorize(creds)
        self.service = discovery.build('sheets', 'v4', credentials=creds)
        self.range_ = 'A1:Z'
        self.SYNC_SUCCESSFUL = "Sync Completed"
        self.SYNC_FAILED = "Sync Failed"
        self.DEFAULT_SYNC_STATUS = "Sync Pending"

    def create_sheet(self):
        sheet = self.client.create('Fyle-GDS')
        return sheet.id

    def share_sheet(self, sheet_id, email_id):
        sheet = self.client.open_by_key(sheet_id)
        sheet.share(email_id, perm_type='user', role='writer')

    def write_data(self, orgs, sheet_id):
        data_to_export, total_orgs = [get_headers()], 0
        for org in orgs.values():
            if org['refresh_token'] is not None:
                fyle_tpa_data = FyleConnector(org['refresh_token'])
                data_to_export += format_expenses(fyle_tpa_data.get_fyle_tpa())
                total_orgs += 1

        value_range_body = {
            'values': data_to_export
        }
        self.service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=self.range_).execute()
        request = self.service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=self.range_,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=value_range_body)
        response = request.execute()
        rows = len(data_to_export)-1
        if response:
            return True, rows, total_orgs
        return False, 0, total_orgs, SYNC_FAILED
