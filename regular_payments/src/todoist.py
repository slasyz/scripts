import logging
import time
from datetime import date, datetime

from requests.exceptions import HTTPError
from todoist_api_python.api import TodoistAPI

from payments import Payment


DATE_FORMAT = '%Y-%m-%d'


def generate_task_text(payment: Payment) -> str:
    actions = ', '.join([x.lower() for x in payment.row.todo])

    source = payment.row.payment_source
    if source == 'С баланса':
        source = 'с баланса'
    elif source == 'Вручную':
        source = 'вручную'
    elif source == '':
        source = 'хз откуда'
    else:
        source = 'с ' + source
    return f'[Оплата] {payment.name} — {payment.row.price} {payment.row.currency} {source} ({actions})'


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


def put(token: str, project_id: str, payments: list[Payment], since: date):
    api = TodoistAPI(token)
    tasks = api.get_tasks(project_id=project_id)

    # Just a dictionary of all tasks in project.
    # Using it to track duplicates.
    all_tasks: dict[tuple[date, str], str] = {}  # all_tasks[when,text][id]
    # Dictionary of all future tasks.
    # Using it to clean up redundant future tasks (for example, tasks that were created as a result of previous modified script run).
    new_tasks: dict[tuple[date, str], str] = {}  # new_tasks[when,text][id]

    # Walking through all existing tasks in the list
    for task in tasks:
        if task.due is None:
            # Just deleting it
            logging.info('-> deleting (no due date): %s [id=%s]', task.content, task.id)
            api.delete_task(task.id)
            continue

        task_date = datetime.strptime(task.due.date, DATE_FORMAT).date()
        if task_date > since:
            new_tasks[task_date, task.content] = task.id

        # We already saw task with the same date and text.  Let's remove it.
        if (task_date, task.content) in all_tasks.keys():
            logging.info('-> duplicate: %s [%s]', task.content, task_date)
            api.delete_task(task.id)
            continue

        all_tasks[task_date, task.content] = task.id

    # Adding new payments
    for payment in payments:
        text = generate_task_text(payment)
        when = payment.when
        when_formatted = datetime.strftime(when, DATE_FORMAT)

        del new_tasks[when, text]

        if (when, text) in all_tasks.keys():
            logging.info('-> already there: %s [%s]', text, when)
            continue

        logging.info('-> adding: %s [%s]', text, when)
        retry_add_task(api, text, project_id, when_formatted)
        time.sleep(0.5)

    # Cleaning up redundant future tasks.
    for key, val in new_tasks.items():
        logging.info('-> deleting: %s [%s] [id=%s]', key[1], key[0], val)
        api.delete_task(val)
        time.sleep(0.5)
