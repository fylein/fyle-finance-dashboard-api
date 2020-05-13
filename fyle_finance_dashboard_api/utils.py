from rest_framework.views import Response
from rest_framework.serializers import ValidationError

def assert_valid(condition: bool, message: str) -> Response or None:
    """
    Assert conditions
    :param condition: Boolean condition
    :param message: Bad request message
    :return: Response or None
    """
    if not condition:
        raise ValidationError(detail={
            'message': message
        })


def format_date(value):
    if value:
        value = value.split("T")[0].split("-")[::-1]
        return "-".join(value)
    return value


FUND_SOURCE = {
    "PERSONAL": "Personal Account",
    "ADVANCE": "Advance",
    "CCC": "Corporate Credit Card"
}

STATES = {
    "PAYMENT_PROCESSING": "Payment Processing",
    "COMPLETE": "Complete",
    "PAYMENT_PENDING": "Payment Pending",
    "APPROVED": "Approved",
    "APPROVER_PENDING": "Approver pending",
    "DRAFT": "Draft",
    "PAID": "Paid"
}

REIMBURSABLE = {
    1: "YES",
    0: "NO"
}


def get_headers():
    header = [
        'Org name',
        'Employee Email',
        'Report Id',
        'Employee Code',
        'Cost Center',
        'Reimbursable',
        'State',
        'Claim Number',
        'Currency',
        'Amount',
        'Purpose',
        'Sub Category',
        'Expense Number',
        'Fund Source',
        'Category Name',
        'Approved on',
        'Spent on',
        'Created At'
    ]
    return header


def format_expenses(expenses):
    formatted_expenses = []
    for expense in expenses:
        formatted_expense = [
            expense['org_name'],
            expense['employee_email'],
            expense['report_id'],
            expense['employee_id'],
            expense['cost_center_name'],
            REIMBURSABLE[expense['reimbursable']],
            STATES[expense['state']],
            expense['claim_number'],
            expense['currency'],
            expense['amount'],
            expense['purpose'],
            expense['sub_category'],
            expense['expense_number'],
            FUND_SOURCE[expense['fund_source']],
            expense['category_name'],
            format_date(expense['approved_at']),
            format_date(expense['spent_at']),
            format_date(expense['created_at'])
        ]
        formatted_expenses.append(formatted_expense)
    return formatted_expenses
