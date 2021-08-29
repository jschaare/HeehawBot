import json


def get_config():
    try:
        with open("config.json") as f:
            cfg = json.load(f)
        return cfg
    except FileNotFoundError:
        raise FileNotFoundError("config not found")
