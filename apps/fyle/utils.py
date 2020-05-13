from django.conf import settings

from fylesdk import FyleSDK


class FyleConnector:
    """
    Fyle utility functions
    """
    def __init__(self, refresh_token):
        client_id = settings.FYLE_CLIENT_ID
        client_secret = settings.FYLE_CLIENT_SECRET
        base_url = settings.FYLE_BASE_URL
        self.connection = FyleSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

    def get_employee_profile(self):
        """
        Get expenses from fyle
        """
        employee_profile = self.connection.Employees.get_my_profile()

        return employee_profile['data']

    def get_expenses(self):
        return self.connection.Expenses.get_all()
