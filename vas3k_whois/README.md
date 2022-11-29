# vas3k_whois

A simple script that sends /whois command from my behalf to everyone joining some chats.


## Preparing

```
$ mkdir ~/deployments/scripts/vas3k_whois
$ mkdir ~/logs/scripts/vas3k_whois

$ wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb
$ dpkg -i libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb
$ rm libssl1.1_1.1.1f-1ubuntu2.16_amd64.deb

$ cd ~/deployments/scripts/vas3k_whois
$ virtualenv ./venv -p python3.11 --download
```

## Deploying

Create config.yml based on `config.example.yml`, and:

```
$ make deploy
```

Then connect to the instance, run script manually, log in to Telegram, and start systemd service again.
