import json

class DataProvider:
    def __init__(self, path="test_data.json") -> None:
        with open(path, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def get(self, prop: str, type_: type = str):
        val = self.data.get(prop)
        if val is None:
            return None
        return type_(val)

    def get_token(self) -> str:
        return self.get("token", str)

    def get_telephone(self) -> str:
        return self.get("telephone", str)