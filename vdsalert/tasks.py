import os

from fabric import Connection
from invoke import task


@task
def deploy(c, t='user@server', project_dir="~/deployments/scripts/vdsalert"):
    conn = Connection(t)

    c.run(f'scp ./url.txt {t}:{os.path.join(project_dir, "url.txt")}')
    c.run(f'scp ./vdsalert.sh {t}:{os.path.join(project_dir, "vdsalert.sh")}')
    c.run(f'scp ./vdsalert.service {t}:~/.config/systemd/user/vdsalert.service')
    c.run(f'scp ./vdsalert.timer {t}:~/.config/systemd/user/vdsalert.timer')

    conn.run('systemctl --user daemon-reload')
    conn.run('systemctl --user enable vdsalert.timer')
    conn.run('systemctl --user start vdsalert.timer')
    conn.run('systemctl --user start vdsalert.service')
