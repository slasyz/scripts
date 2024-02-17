import sqlite3
import csv
from datetime import datetime
import os

DB_FILENAME = 'resources/moneywiz.sqlite3'
CSV_FILENAME = 'resources/moneywiz.csv'

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
}

# TODO: добавить пометку со страной в которой находился в этот день


if os.path.exists(DB_FILENAME):
    os.remove(DB_FILENAME)

# Connect to SQLite database
conn = sqlite3.connect(DB_FILENAME)
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
    )
''')

# Open the CSV file and insert data into database
with open(CSV_FILENAME, 'r') as file:
    csvReader = csv.reader(file)
    next(csvReader)  # Skip header row
    next(csvReader)  # Skip header row

    for row in csvReader:
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

print('Data inserted successfully')
