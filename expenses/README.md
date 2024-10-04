# expenses

Converts a MoneyWiz csv file to a SQLite database.

## Usage

1. Export csv file from MoneyWiz to `resources/moneywiz.csv`

2. Export NomadList data to `resources/nomadlist.csv`

3. Run `poetry run python expenses/script.py` to generate `moneywiz.sqlite3`

4. Check its content using `litecli resources/moneywiz.sqlite3` or `sqlite3 resources/moneywiz.sqlite3`

5. Copy it to Metabase: `scp resources/moneywiz.sqlite3 hetzner-1:~/deployments/metabase/data/`
