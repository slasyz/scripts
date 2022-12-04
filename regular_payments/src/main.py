import datetime
import logging
import time

from dateutil.relativedelta import relativedelta
import requests

import config
import sheet
from payments import generate_payments
import todoist


def step():
    logging.info('')
    logging.info('*** parsing table')
    c = config.load()
    rows = sheet.read_from_spreadsheet(c['sheet_id'])

    for row in rows:
        logging.info('-> %s | %s | %s %s / %s | %s | %s | %s',
                     row.category, row.name, row.price, row.currency, row.period, row.when, row.payment_source, row.todo)

    since = datetime.date.today() + relativedelta(days=1)
    until = since + relativedelta(months=1)

    logging.info('')
    logging.info(f'*** generating payments from {since} to {until}')
    payments = generate_payments(rows, since, until)
    for payment in payments:
        logging.info('-> %s [%s]', payment.name, payment.when)

    logging.info('')
    logging.info(f'*** adding everything to Todoist')
    todoist.put(c['todoist_token'], c['todoist_project_id'], payments, since)

    logging.info('')
    requests.get(c['uptime_url'])


def main():
    FORMAT = '%(asctime)s %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO)

    while True:
        step()
        logging.info('')
        logging.info('*** sleeping 24h...')
        time.sleep(24 * 60 * 60)


if __name__ == '__main__':
    main()
