import os.path
import sqlite3
import csv
from datetime import datetime


rates = {
    'USD': 1,
    'VND': 24530,
    'RUB': 92.5,
    'EUR': 0.93,
    'TRY': 30.84,
    'GEL': 2.64,
    'KGS': 89.43,
    'HKD': 7.82,
    'MYR': 4.78,
    'AZN': 1.7,
    'KRW': 1333,
    'SGD': 1.35,
    'IDR': 15655,
    'THB': 35.75,
    'TWD': 32.18,
}


def convert(mw_filename: str, sqlite_filename: str):
    mw_filename = os.path.expanduser(mw_filename)
    sqlite_filename = os.path.expanduser(sqlite_filename)

    # Connect to SQLite database
    conn = sqlite3.connect(sqlite_filename)
    cursor = conn.cursor()

    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions
        (
            account TEXT,
            description TEXT,
            payee TEXT,
            category TEXT,
            subcategory TEXT,
            date DATE,
            time TIME,
            memo TEXT,
            amount REAL,
            currency TEXT,
            tags TEXT,
            amount_usd REAL
        );
    ''')

    cursor.execute('DELETE FROM transactions')

    # Open the CSV file and insert data into database
    with open(mw_filename, 'r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # Skip header row

        for row in csv_reader:
            name, current_balance, account, transfers, description, payee, category, date, time, memo, amount, currency, check_number, tags = row

            if current_balance != '':
                continue
            if transfers != '':
                continue
            if description == 'New balance':
                continue
            if category == 'Salary':
                continue

            amount = amount.replace(',', '.').replace("\xa0", '')
            amount = -float(amount)
            date = datetime.strptime(date, '%d/%m/%Y').strftime('%Y-%m-%d')
            amount_usd = float(amount) / rates[currency]
            subcategory = ''

            if '▶︎' in category:
                category, subcategory = category.split('▶︎')
                category = category.strip()
                subcategory = subcategory.strip()

            cursor.execute(
                '''INSERT INTO transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?)''',
                [account, description, payee, category, subcategory, date, time, memo, amount, currency, tags, amount_usd]
            )

    # Commit changes and close connection
    conn.commit()
    conn.close()
