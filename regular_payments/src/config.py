import os

import yaml

config_filename = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../config.yml')


def load_google_credentials() -> str:
    with open(config_filename, 'r') as f:
        config = yaml.safe_load(f)
        return config['google_credentials']


def load_google_token() -> str | None:
    with open(config_filename, 'r') as f:
        config = yaml.safe_load(f)
        try:
            return config['google_token']
        except KeyError:
            return None


def save_google_token(token: str):
    with open(config_filename, 'r') as f:
        config = yaml.safe_load(f)
    config['google_token'] = token
    with open(config_filename, 'w') as f:
        yaml.safe_dump(config, f)


def load():
    with open(config_filename, 'r') as f:
        return yaml.safe_load(f)
