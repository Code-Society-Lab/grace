import json


class JsonConfig:
    def __init__(self, json_config):
        self.config = json_config
        self.extensions = None

        for key in json_config.keys():
            value = json_config.get(key)

            setattr(self, key, JsonConfig(value) if isinstance(value, dict) else value)

    def load_extensions_configs(self, extensions_configs):
        json_extensions = {}

        for extension_configs in extensions_configs:
            with open(extension_configs) as extensions_config_file:
                json_extensions.update(json.load(extensions_config_file))

        self.extensions = JsonConfig(json_extensions)

    @staticmethod
    def load_file(file):
        with open(file) as config_file:
            return JsonConfig(json.load(config_file))
