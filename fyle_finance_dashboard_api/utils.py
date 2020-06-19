from rest_framework.views import Response
from rest_framework.serializers import ValidationError
import requests
import json
from datetime import date, timedelta

MONTHS = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'June',
    'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec'
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


def get_exchange_rates(start_date, end_date, currency):
    global all_exchange_rates
    currency_exchange_rates = requests.get(
        'https://api.exchangeratesapi.io/history?start_at={}&end_at={}&base=USD&symbols=USD,{}'.format(
            start_date, end_date, currency))
    all_exchange_rates[currency] = json.loads(currency_exchange_rates.text)["rates"]


def get_single_date_exchange_rate(exchange_date, currency):
    global all_exchange_rates
    exchange_date_to_int = [*map(int, exchange_date.split("-"))]
    datetime_object = date(exchange_date_to_int[0], exchange_date_to_int[1], exchange_date_to_int[2])
    one_day_before_exchange_date = str((datetime_object - timedelta(days=1)).strftime('%Y-%m-%d'))
    two_days_before_exchange_date = str((datetime_object - timedelta(days=2)).strftime('%Y-%m-%d'))
    if one_day_before_exchange_date in all_exchange_rates[currency]:
        all_exchange_rates[currency][exchange_date] = {
            currency: all_exchange_rates[currency][one_day_before_exchange_date][currency],
            'USD': all_exchange_rates[currency][one_day_before_exchange_date]['USD']
        }
        return

    if two_days_before_exchange_date in all_exchange_rates[currency]:
        all_exchange_rates[currency][exchange_date] = {
            currency: all_exchange_rates[currency][two_days_before_exchange_date][currency],
            'USD': all_exchange_rates[currency][two_days_before_exchange_date][currency]
        }
        return
    currency_exchange_rates = requests.get('https://api.exchangeratesapi.io/{}?base=USD'.format(exchange_date))
    total_exchange_rates = json.loads(currency_exchange_rates.text)["rates"]
    all_exchange_rates[currency][exchange_date] = {
        currency: total_exchange_rates[currency] if currency in total_exchange_rates else None,
        'USD': total_exchange_rates['USD']
    }


def format_date(value, currency=False):
    if value:
        date_string, month, year = value.split("T")[0].split("-")[::-1]
        if not currency:
            return "{} {}, {}".format(MONTHS[int(month) - 1], date_string, year)
        else:
            return "{}-{}-{}".format(year, month, date_string)
    return value


def calculate_amount(expense, start_date, end_date):
    global all_exchange_rates
    created_at = format_date(expense['created_at'], True)
    spent_at = format_date(expense['spent_at'], True)
    currency = expense['currency']
    amount = expense['amount']
    exchange_rate_date = spent_at
    if exchange_rate_date is None:
        exchange_rate_date = created_at
    if currency is not None:
        if currency not in all_exchange_rates:
            get_exchange_rates(start_date, end_date, currency)
        if exchange_rate_date not in all_exchange_rates[currency]:
            get_single_date_exchange_rate(exchange_rate_date, currency)
        currency_rate = all_exchange_rates[currency][exchange_rate_date][currency]
        return round(amount / currency_rate, 2) if currency_rate is not None else None
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
        'Employee Id',
        'Cost Center',
        'Reimbursable',
        'State',
        'Report Number',
        'Currency',
        'Amount',
        'Amount in USD',
        'Purpose',
        'Expense Number',
        'Fund Source',
        'Category Name',
        'Sub Category',
        'Project Name',
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
            expense['employee_code'],
            expense['cost_center_name'],
            "YES" if expense['reimbursable'] else "NO",
            STATES[expense['state']],
            expense['claim_number'],
            expense['currency'],
            expense['amount'],
            expense['amount'] if expense['currency'] == 'USD' else calculate_amount(expense,
                                                                         start_date, end_date),
            expense['purpose'],
            expense['expense_number'],
            FUND_SOURCES[expense['fund_source']],
            expense['category_name'],
            expense['sub_category'],
            expense['project_name'],
            format_date(expense['spent_at']),
            format_date(expense['created_at']),
            format_date(expense['approved_at'])
        ]
        formatted_expenses.append(formatted_expense)
    return formatted_expenses
