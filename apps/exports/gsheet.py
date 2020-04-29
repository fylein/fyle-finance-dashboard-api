from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import gspread
import os


class GoogleSpreadSheet:
    def __init__(self):
        scope = [
            'https://www.googleapis.com/auth/analytics.readonly',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)

        self.client = gspread.authorize(creds)

    def create_sheet(self, share_with):
        sheet = self.client.create('Fyle-GDS')
        sheet.share(share_with, perm_type='user', role='writer')
        return sheet.id

    def write_data(self, data, sheet_id):
        self.client.import_csv(sheet_id, data)
        return True
