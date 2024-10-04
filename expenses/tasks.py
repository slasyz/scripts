from time import sleep

from invoke import task  # type: ignore
from fabric import Connection  # type: ignore


def exec(c, cmd):
    host = c.host if isinstance(c, Connection) else 'localhost'
    print(f'--- {host} --- $ {cmd}')
    c.run(cmd)


@task
def upload(c, target="hetzner-1"):
    project_dir = "~/deployments/scripts/expenses"
    logs_prefix = "~/logs/expenses"

    print('\n*** copying files...')
    exec(c, f"rsync -av --delete ./expenses/ {target}:{project_dir}/expenses/")
    exec(c, f"scp ./resources/nomadlist.csv {target}:{project_dir}/nomadlist.csv")
    exec(c, f"scp ./pyproject.toml ./poetry.lock {target}:{project_dir}/")
    exec(c, f"scp ./expenses.service {target}:~/.config/systemd/user/expenses.service")

    print('\n*** running commands on target machine...')
    conn = Connection(target)
    exec(conn, f"cd {project_dir} && poetry install --no-root")
    exec(conn, f"chmod 0644 ~/.config/systemd/user/expenses.service")
    exec(conn, f'sed -i "s|{{{{ logs_prefix }}}}|$(readlink -f {logs_prefix})|g" ~/.config/systemd/user/expenses.service')
    exec(conn, f'sed -i "s|{{{{ project_dir }}}}|$(readlink -f {project_dir})|g" ~/.config/systemd/user/expenses.service')
    exec(conn, f'sed -i "s|{{{{ home_dir }}}}|$HOME|g" ~/.config/systemd/user/expenses.service')

    print('\n*** restarting service...')
    exec(conn, "systemctl --user daemon-reload")
    exec(conn, "systemctl --user enable expenses")
    exec(conn, "systemctl --user restart expenses")
    exec(conn, "systemctl --user status expenses")
    sleep(2)
    exec(conn, f"tail -n 10 {logs_prefix}.log")
