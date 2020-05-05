from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import gspread

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

    def create_sheet(self, share_with):
        share_with = 'sheshant.sinha@fyle.in'
        sheet = self.client.create('Fyle-GDS')
        sheet.share(share_with, perm_type='user', role='writer')
        return sheet.id

    def write_data(self, data, sheet_id):
        value_range_body = {
            'values': data
        }
        self.service.spreadsheets().values().clear(spreadsheetId=sheet_id, range=self.range_).execute()
        request = self.service.spreadsheets().values().append(
            spreadsheetId=sheet_id,
            range=self.range_,
            valueInputOption='RAW',
            insertDataOption='INSERT_ROWS',
            body=value_range_body)
        response = request.execute()

        return response
