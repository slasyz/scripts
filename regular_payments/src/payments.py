from dataclasses import dataclass
from datetime import date

from dateutil.relativedelta import relativedelta

from spreadsheet import Row


@dataclass
class Payment:
    name: str
    row: Row
    when: date


PERIODS = {
    'Месяц': relativedelta(months=1),
    'Полгода': relativedelta(months=6),
    '2 года': relativedelta(years=2),
    'Год': relativedelta(years=1),
}


def generate_payments(rows: list[Row], since: date, until: date) -> list[Payment]:
    res: list[Payment] = []
    for row in rows:
        current = row.when
        while current <= until:
            if current < since:
                current = current + PERIODS[row.period]
                continue

            payment = Payment(
                name=row.name,
                row=row,
                when=current,
            )
            res.append(payment)

            current = current + PERIODS[row.period]

    res = sorted(res, key=lambda x: x.when)
    return res
