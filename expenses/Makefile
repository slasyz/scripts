update:
	poetry run python expenses/script.py && \
		litecli resources/moneywiz.sqlite3 && \
		scp resources/moneywiz.sqlite3 hetzner-1:~/deployments/metabase/data/
