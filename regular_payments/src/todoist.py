import logging
import time
from datetime import date, datetime

from requests.exceptions import HTTPError
from todoist_api_python.api import TodoistAPI

from payments import Payment


DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_HUMAN = '%d %b %Y'


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

    date_str = datetime.strftime(payment.when, DATE_FORMAT_HUMAN)
    return f'[{date_str}] {payment.name} — {payment.row.price} {payment.row.currency} {source} ({actions})'


def get_date_from_text(text: str) -> datetime | None:
    if not text.startswith('['):
        return None
    text = text[1:]

    i = text.find(']')
    if i == -1:
        return None
    text = text[:i]

    try:
        return datetime.strptime(text, DATE_FORMAT_HUMAN).date()
    except ValueError:
        return None


def retry_add_task(api: TodoistAPI, text: str, project_id: str):
    while True:
        try:
            api.add_task(
                content=text,
                project_id=project_id,
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
        if task.due is not None:
            # Just deleting it, something old
            logging.info('-> deleting (with due date): %s [id=%s]', task.content, task.id)
            api.delete_task(task.id)
            continue

        task_date = get_date_from_text(task.content)
        if task_date is None:
            # Deleting, invalid date
            logging.info('-> deleting (invalid date): %s [id=%s]', task.content, task.id)
            api.delete_task(task.id)
            continue

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

        try:
            del new_tasks[when, text]
        except KeyError:
            pass

        if (when, text) in all_tasks.keys():
            logging.info('-> already there: %s [%s]', text, when)
            continue

        logging.info('-> adding: %s [%s]', text, when)
        retry_add_task(api, text, project_id)
        time.sleep(0.5)

    # Cleaning up redundant future tasks.
    for key, val in new_tasks.items():
        logging.info('-> deleting: %s [%s] [id=%s]', key[1], key[0], val)
        api.delete_task(val)
        time.sleep(0.5)
