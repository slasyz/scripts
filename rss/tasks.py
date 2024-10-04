from time import sleep

from invoke import task  # type: ignore
from fabric import Connection  # type: ignore


def exec(c, cmd):
    host = c.host if isinstance(c, Connection) else 'localhost'
    print(f'--- {host} --- $ {cmd}')
    c.run(cmd)


@task
def deploy(c, target="hetzner-1"):
    print('\n*** building for linux/amd64...')
    exec(c, "GOOS=linux GOARCH=amd64 go build -o rss")

    conn = Connection(target)

    print('\n*** copying files...')
    exec(conn, "mkdir -p ~/deployments/scripts/rss")
    exec(c, f"scp ./rss ./config.json {target}:~/deployments/scripts/rss")
    exec(c, f"scp ./rss.service ./rss.timer {target}:~/.config/systemd/user/")

    print('\n*** running commands on target machine...')
    exec(conn, f"chmod 0700 ~/deployments/scripts/rss/rss")
    exec(conn, f"chmod 0644 ~/.config/systemd/user/rss.service")
    exec(conn, f"chmod 0644 ~/.config/systemd/user/rss.timer")
    exec(c, f"scp ./Caddyfile {target}:~/caddy/rss.caddy")

    print('\n*** restarting everything...')
    exec(conn, "systemctl --user daemon-reload")
    exec(conn, "systemctl --user enable rss.timer")
    exec(conn, "systemctl --user restart rss.timer")
    exec(conn, "systemctl --user start rss.service")
    exec(conn, "systemctl --user status rss.timer")
    exec(conn, "systemctl --user status rss.service")
    exec(conn, "sudo -S systemctl restart caddy")
    sleep(2)
