from rest_framework.views import Response
from rest_framework.serializers import ValidationError
import requests
import json

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "June",
          "July", "Aug", "Sept", "Oct", "Nov", "Dec"
          ]
all_exchange_rates = {}


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


def get_exchange_rate(start_date, end_date, currency):
    global all_exchange_rates
    currency_exchange_rates = requests.get(
        'https://api.exchangeratesapi.io/history?start_at={}&end_at={}&symbols=USD,{}'.format(start_date, end_date,
                                                                                              currency))
    all_exchange_rates[currency] = json.loads(currency_exchange_rates.text)["rates"]


def get_single_date_exchange_rate(date, currency):
    global all_exchange_rates
    currency_exchange_rates = requests.get('https://api.exchangeratesapi.io/{}?base=USD'.format(date))
    total_exchange_rates = json.loads(currency_exchange_rates.text)["rates"]
    all_exchange_rates[currency][date] = {
        currency: total_exchange_rates[currency],
        'USD': total_exchange_rates['USD']
    }


def format_date(value, currency=False):
    if value:
        date, month, year = value.split("T")[0].split("-")[::-1]
        if not currency:
            return "{} {}, {}".format(MONTHS[int(month) - 1], date, year)
        else:
            return "{}-{}-{}".format(year, month, date)
    return value


def calculate_amount(created_at, start_date, end_date, currency, amount):
    global all_exchange_rates
    if currency is not None:
        if currency not in all_exchange_rates:
            get_exchange_rate(start_date, end_date, currency)
        if created_at not in all_exchange_rates[currency]:
            get_single_date_exchange_rate(created_at, currency)
        usd_rate = all_exchange_rates[currency][created_at]['USD']
        currency_rate = all_exchange_rates[currency][created_at][currency]
        return (usd_rate * amount) / currency_rate
    return None


FUND_SOURCES = {
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


def get_headers():
    header = [
        'Entity Name',
        'Employee Email',
        'Report Id',
        'Employee Id',
        'Cost Center',
        'Reimbursable',
        'State',
        'Claim Number',
        'Currency',
        'Amount',
        'Amount in USD',
        'Purpose',
        'Expense Number',
        'Fund Source',
        'Category Name',
        'Sub Category',
        'Spent On',
        'Created On',
        'Approved On'
    ]
    return header


def format_expenses(expenses):
    formatted_expenses = []
    expenses = sorted(expenses, key=lambda x: format_date(x['created_at'], True))
    start_date = format_date(expenses[0]['created_at'], True)
    end_date = format_date(expenses[-1]['created_at'], True)

    for expense in expenses:
        formatted_expense = [
            expense['org_name'],
            expense['employee_email'],
            expense['report_id'],
            expense['employee_id'],
            expense['cost_center_name'],
            "YES" if expense['reimbursable'] else "NO",
            STATES[expense['state']],
            expense['claim_number'],
            expense['currency'],
            expense['amount'],
            expense['amount'] if expense['currency'] == 'USD' else calculate_amount(format_date(expense['created_at'], True),
                                                                         start_date, end_date, expense['currency'],
                                                                         expense['amount']),
            expense['purpose'],
            expense['expense_number'],
            FUND_SOURCES[expense['fund_source']],
            expense['category_name'],
            expense['sub_category'],
            format_date(expense['spent_at']),
            format_date(expense['created_at']),
            format_date(expense['approved_at'])
        ]
        formatted_expenses.append(formatted_expense)
    return formatted_expenses
