from fylesdk import FyleSDK
import os

class FyleTpaData:
    def __init__(self, refresh_token):
        client_id = os.environ['FYLE_CLIENT_ID']
        client_secret = os.environ['FYLE_CLIENT_SECRET']
        self.conn = FyleSDK(
            base_url='https://staging.fyle.in',
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token
        )

    def fyle_tpa(self):
        return self.conn.Expenses.get_all()


class FormatData:
    def __init__(self):
        self.keys = [
            "employee_email",
            "employee_id",
            "spent_at",
            "currency",
            "amount",
            "purpose",
            "cost_center_name",
            "category_name",
            "sub_category",
            "expense_number",
            "report_id",
            "state",
            "fund_source",
            "reimbursable",
            "created_at",
            "approved_at",
            "org_name",
            "claim_number"
        ]

        self.map = {
            "employee_email": "Employee Email",
            "employee_id": "Employee Code",
            "spent_at": "Spent on",
            "currency": "Currency",
            "amount": "Amount",
            "purpose": "Purpose",
            "cost_center_name": "Cost Center",
            "category_name": "Category",
            "sub_category": "Sub Category",
            "expense_number": "Expense Number",
            "report_id": "Report Id",
            "state": "State",
            "fund_source": "Fund Source",
            "reimbursable": "Reimbursable",
            "created_at": "Created on",
            "approved_at": "Approved on",
            "org_name": "Org name",
            "claim_number": "Claim Number"
        }

        self.value_casting = {
            "spent_at": self.cast_date,
            "created_at": self.cast_date,
            "approved_at": self.cast_date,
            "fund_source": self.fund_source,
            "reimbursable": self.reimbursable,
            "state": self.state,
        }

    def fund_source(self,value):
        if value == "PERSONAL":
            value = "Personal Account"
        elif value == "ADVANCE":
            value = "Advance"
        return value

    def cast_date(self, value):
        if value:
            value = value.split("T")[0].split("-")[::-1]
            return "-".join(value)
        return value

    def state(self, value):
        if value == "PAYMENT_PROCESSING":
            value = "Payment Processing"
        elif value == "COMPLETE":
            value = "Complete"
        elif value == "PAYMENT_PENDING":
            value = "Payment Pending"
        elif value == "APPROVED":
            value = "Approved"
        elif value == "APPROVER_PENDING":
            value = "Approver pending"
        return value

    def reimbursable(self, value):
        if value:
            value = "YES"
        else:
            value = "NO"
        return value

    def headers(self):
        return [self.map[head] for head in self.keys]

    def formatting_specific_key(self, key, value):
        if key in self.value_casting:
            value = self.value_casting[key](value)
        return value

    def format(self, tpas):
        return [[self.formatting_specific_key(key, tpa[key]) for key in self.keys] for tpa in tpas]
