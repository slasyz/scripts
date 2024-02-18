from invoke import task
from fabric import Connection

def exec(c, cmd):
    host = c.host if isinstance(c, Connection) else 'localhost'
    print(f'--- {host} --- $ {cmd}')
    c.run(cmd)

@task
def run(c):
    c.run("poetry run python src/main.py")

@task
def loop(c):
    c.run("poetry run python src/main.py --loop")

@task
def upload(c, target="hetzner-1"):
    project_dir = "~/deployments/scripts/regular_payments"
    logs_prefix = "~/logs/regular_payments"

    print('\n*** copying files...')
    exec(c, f"rsync -av --delete ./src/ {target}:{project_dir}/src/")
    exec(c, f"scp ./config.yml {target}:{project_dir}/config.yml")
    exec(c, f"scp ./pyproject.toml ./poetry.lock {target}:{project_dir}/")
    exec(c, f"scp ./regular-payments.service {target}:~/.config/systemd/user/regular-payments.service")

    print('\n*** running commands on target machine...')
    conn = Connection(target)
    exec(conn, f"cd {project_dir} && poetry install --no-root")
    exec(conn, f"chmod 0644 ~/.config/systemd/user/regular-payments.service")
    exec(conn, f'sed -i "s|{{{{ logs_prefix }}}}|$(readlink -f {logs_prefix})|g" ~/.config/systemd/user/regular-payments.service')
    exec(conn, f'sed -i "s|{{{{ project_dir }}}}|$(readlink -f {project_dir})|g" ~/.config/systemd/user/regular-payments.service')

    exec(conn, f'sed -i "s|{{{{ home_dir }}}}|$HOME|g" ~/.config/systemd/user/regular-payments.service')

    print('\n*** restarting service...')
    exec(conn, "systemctl --user daemon-reload")
    exec(conn, "systemctl --user enable regular-payments")
    exec(conn, "systemctl --user restart regular-payments")
