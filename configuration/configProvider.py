import configparser
import os
from typing import Optional, Union

_config = None

def _load_config():
    global _config
    if _config is None:
        # Ищем конфиг в нескольких местах
        possible_paths = [
            os.environ.get("CHITAI_CONFIG"),  # из переменной окружения
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.ini"),  # рядом с файлом
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "settings.ini"),  # в корне проекта
        ]
        
        parser = configparser.ConfigParser()
        
        for config_path in possible_paths:
            if config_path and os.path.exists(config_path):
                parser.read(config_path, encoding="utf-8")
                _config = parser
                return _config
        
        # Если ничего не нашли, создаем пустой конфиг
        _config = parser
    return _config

class configProvider:
    def __init__(self) -> None:
        self.config = _load_config()
    
    def get(self, section: str, prop: str, fallback: Optional[str] = None) -> str:
        """Получить строковое значение"""
        try:
            return self.config.get(section, prop)
        except (configparser.NoSectionError, configparser.NoOptionError):
            if fallback is not None:
                return fallback
            raise
    
    def getint(self, section: str, prop: str, fallback: Optional[int] = None) -> int:
        """Получить целочисленное значение"""
        try:
            return self.config.getint(section, prop)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def getboolean(self, section: str, prop: str, fallback: Optional[bool] = None) -> bool:
        """Получить булево значение"""
        try:
            return self.config.getboolean(section, prop)
        except (configparser.NoSectionError, configparser.NoOptionError, ValueError):
            if fallback is not None:
                return fallback
            raise
    
    def get_ui_url(self) -> str:
        """Получить URL для UI тестов"""
        return self.get("ui", "base_url").rstrip("/")
    
    def get_api_config(self) -> dict:
        """Получить конфигурацию для API"""
        return {
            "base_url": self.get("api", "base_url", "https://www.chitai-gorod.ru/api"),
            "token": self.get("api", "token", ""),
            "token_type": self.get("api", "token_type", "header")
        }
    
    def get_search_limit(self) -> int:
        """Получить лимит поиска"""
        return self.getint("search", "default_limit", 20)