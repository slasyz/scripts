import json
from dataclasses import dataclass
from datetime import date, datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config


# If modifying these scopes, remove token from config.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
RANGE = 'Main!A2:J'

MONTHS = {
    'января': 'jan',
    'февраля': 'feb',
    'марта': 'mar',
    'апреля': 'apr',
    'мая': 'may',
    'июня': 'jun',
    'июля': 'jul',
    'августа': 'aug',
    'сентября': 'sep',
    'октября': 'oct',
    'ноября': 'nov',
    'декабря': 'dec',
}


@dataclass
class Row:
    category: str
    name: str
    price: int
    currency: str
    period: str
    rub_in_period: int
    rub_in_month: int
    when: date
    payment_source: str
    todo: list[str]


def load():
    creds = None
    # The token stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    token = config.load_google_token()
    if token is not None:
        creds = Credentials.from_authorized_user_info(json.loads(token), SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials = json.loads(config.load_google_credentials())
            flow = InstalledAppFlow.from_client_config(credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        config.save_google_token(creds.to_json())

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    return sheet


def read_from_spreadsheet(sheet_id: str) -> list[Row]:
    sheet = load()
    result = sheet.values().get(spreadsheetId=sheet_id,
                                range=RANGE).execute()
    values = result.get('values', [])

    if not values:
        raise Exception('no data found')

    res: list[Row] = []
    for row in values:
        if row[0] == '':
            break

        when = row[7]
        for key, val in MONTHS.items():
            when = when.replace(key, val)
        when = datetime.strptime(when, '%d %b %Y').date()

        todo = row[9].split('/')

        row = Row(
            category=row[0],
            name=row[1],
            price=row[2],
            currency=row[3],
            period=row[4],
            rub_in_period=row[5],
            rub_in_month=row[6],
            when=when,
            payment_source=row[8],
            todo=todo,
        )
        res.append(row)

    return res
