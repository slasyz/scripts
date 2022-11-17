import logging
import time
from datetime import date, datetime

from requests.exceptions import HTTPError
from todoist_api_python.api import TodoistAPI

from payments import Payment


DATE_FORMAT = '%Y-%m-%d'


def generate_task_text(payment: Payment) -> str:
    action = ', '.join([x.lower() for x in payment.row.todo])

    source = payment.row.payment_source
    if source == 'С баланса':
        source = ' с баланса'
    else:
        source = ' с ' + source
    return '[Оплата] ' + payment.name + source + ' (' + action + ')'


def retry_add_task(api: TodoistAPI, text: str, project_id: str, when_formatted: str):
    while True:
        try:
            api.add_task(
                content=text,
                project_id=project_id,
                due_date=when_formatted,
            )
            return
        except HTTPError as ex:
            if '502 Server Error' in ex.response.text:
                logging.info('-> retrying because of 502')
                continue
            raise


def put(token: str, project_id: str, payments: list[Payment]):
    api = TodoistAPI(token)
    tasks = api.get_tasks(project_id=project_id)

    tasks_by_date: dict[tuple[date, str], str] = {}  # tasks_by_date[when,text][id]

    for task in tasks:
        if task.due is None:
            logging.info('-> deleting (no due date): %s [id=%s]', task.content, task.id)
            api.delete_task(task.id)
            continue

        task_date = datetime.strptime(task.due.date, DATE_FORMAT).date()
        if (task_date, task.content) in tasks_by_date.keys():
            logging.info('-> duplicate: %s [%s]', task.content, task_date)
            api.delete_task(task.id)
            continue

        tasks_by_date[task_date, task.content] = task.id

    for payment in payments:
        text = generate_task_text(payment)
        when = payment.when
        when_formatted = datetime.strftime(when, DATE_FORMAT)

        if (when, text) in tasks_by_date.keys():
            logging.info('-> already there: %s [%s]', text, when)
            del tasks_by_date[when, text]
            continue

        logging.info('-> adding: %s [%s]', text, when)
        retry_add_task(api, text, project_id, when_formatted)
        time.sleep(0.5)

    for key, val in tasks_by_date.items():
        logging.info('-> deleting: %s [%s] [id=%s]', key[1], key[0], val)
        api.delete_task(val)
        time.sleep(0.5)
