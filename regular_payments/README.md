# regular_payments

A simple script that reads my Google Spreadsheet and creates tasks based on it.


## Preparing

```
$ mkdir ~/deployments/scripts/regular_payments
$ mkdir ~/logs/scripts/regular_payments

$ cd ~/deployments/scripts/regular_payments
$ virtualenv ./venv -p python3.11 --download
```

## Deploying

Create config.yml based on `config.example.yml`, and:

```
$ make deploy
```
