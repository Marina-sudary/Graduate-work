import configparser
import os

_config = None

def _load_config():
    global _config
    if _config is None:
        config_path = os.environ.get(
            "CHITAI_CONFIG",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "settings.ini")
        )
        parser = configparser.ConfigParser()
        if os.path.exists(config_path):
            parser.read(config_path, encoding="utf-8")
        _config = parser
    return _config

class configProvider:

    def __init__(self) -> None:
        self.config = _load_config()

    def get(self, section: str, prop: str):
        return self.config.get(section, prop)

    def getint(self, section: str, prop: str):
        return self.config.getint(section, prop)

    def get_ui_url(self) -> str:
        return self.config.get("ui", "base_url")