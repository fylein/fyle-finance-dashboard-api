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

def fund_source(value):
    if value == "PERSONAL":
        value = "Personal Account"
    elif value == "ADVANCE":
        value = "Advance"
    return value


def cast_date(value):
    if value:
        value = value.split("T")[0].split("-")[::-1]
        return "-".join(value)
    return value


def state(value):
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


def reimbursable(value):
    if value:
        value = "YES"
    else:
        value = "NO"
    return value

keys = [
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

map = {
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

value_casting = {
    "spent_at": cast_date,
    "created_at": cast_date,
    "approved_at": cast_date,
    "fund_source": fund_source,
    "reimbursable": reimbursable,
    "state": state
}


def headers():
    return [map[head] for head in keys]


def formatting_specific_key(key, value):
    if key in value_casting:
        value = value_casting[key](value)
    return value


def format_tpa(tpas):
    return [[formatting_specific_key(key, tpa[key]) for key in keys] for tpa in tpas]
