import json


class Config:
    def __init__(self, json_config):
        self.config = json_config

        for key in json_config.keys():
            value = json_config.get(key)

            setattr(self, key, Config(value) if isinstance(value, dict) else value)

    @staticmethod
    def load_file(file):
        with open(file) as config_file:
            return Config(json.load(config_file))
