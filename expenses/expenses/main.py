import os
from convert import convert


DB_FILENAME = 'resources/moneywiz.sqlite3'
CSV_FILENAME = 'resources/moneywiz.csv'
NL_FILENAME = 'resources/nomadlist.csv'


if os.path.exists(DB_FILENAME):
    os.remove(DB_FILENAME)


convert(CSV_FILENAME, NL_FILENAME, DB_FILENAME)


print('Data inserted successfully')
