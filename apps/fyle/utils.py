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
        jobs_url = settings.JOBS_URL
        self.connection = FyleSDK(
            base_url=base_url,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            jobs_url=jobs_url
        )

    def get_employee_profile(self):
        """
        Get expenses from fyle
        """
        employee_profile = self.connection.Employees.get_my_profile()

        return employee_profile['data']

    def get_expenses(self):
        return self.connection.Expenses.get_all()

    def trigger_job(self, callback_url: str, callback_method: str, org_user_id: str,
                    job_description: str, object_id: str, payload: any = None,
                    job_data_url: str = None):
        return self.connection.Jobs.trigger_now(
            callback_url=callback_url,
            callback_method=callback_method,
            org_user_id=org_user_id,
            job_description=job_description,
            object_id=object_id,
            payload=payload,
            job_data_url=job_data_url
        )
