import os
from convert import convert


DB_FILENAME = 'resources/moneywiz.sqlite3'
CSV_FILENAME = 'resources/moneywiz.csv'


convert(CSV_FILENAME, DB_FILENAME)


print('Data inserted successfully')
