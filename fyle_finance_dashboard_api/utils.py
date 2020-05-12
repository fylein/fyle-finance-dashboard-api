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


def get_date(value):
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

EXPENSE_COLUMN_NAMES = {
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

get_value_from_dict = {
    "fund_source": FUND_SOURCE,
    "reimbursable": REIMBURSABLE,
    "state": STATES
}

get_value_from_function = {
    "spent_at": get_date,
    "created_at": get_date,
    "approved_at": get_date
}


def get_headers():
    return [head for head in EXPENSE_COLUMN_NAMES]


def formatting_specific_key(key, value):
    if key in value_casting:
        value = value_casting[key](value)
    return value


def format_expenses(expenses):
    data_to_export = []
    for expense in expenses:
        single_expense = []
        for column_name in EXPENSE_COLUMN_NAMES:
            column_value = expense[column_name]
            if column_name in get_value_from_dict:
                column_value = get_value_from_dict[column_name].get(expense[column_name], expense[column_name])
            if column_name in get_value_from_function:
                column_value = get_date(expense[column_name])
            single_expense.append(column_value)
        data_to_export.append(single_expense)

    return data_to_export
