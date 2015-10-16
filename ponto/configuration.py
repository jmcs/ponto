import yaml

from .paths import CONFIG_PATH


# TODO config class


def open_configuration() -> dict:
    with CONFIG_PATH.open() as config_file:
        config = yaml.load(config_file)
    return config


def save_configuration(data):
    with CONFIG_PATH.open('w') as config_file:
        yaml.safe_dump(data, config_file, default_flow_style=False)
