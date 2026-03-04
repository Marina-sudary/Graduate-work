import json
from typing import List, Dict, Optional
import requests
import os

class ProductApi:
    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        token_type: str = "header"  # "header" или "cookie"
    ) -> None:
        """
        base_url: базовый URL API, например https://www.chitai-gorod.ru/api
        token: токен авторизации
        token_type: способ передачи токена: 'header' (Bearer) или 'cookie'
        """
        self.base_url = (base_url or "https://www.chitai-gorod.ru/api").rstrip("/")
        self.session = requests.Session()
        if token:
            if token_type == "header":
                self.session.headers.update({"Authorization": f"Bearer {token}"})
            elif token_type == "cookie":
                # Пример: передать токен как cookie (название зависит от вашего API)
                self.session.cookies.set("token", token, path="/")
            else:
                raise ValueError("token_type must be 'header' or 'cookie'")
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        path = path.lstrip("/")
        return f"{self.base_url}/{path}"

    def get_product(self, product_id: str) -> Dict:
        """
        Получить карточку товара по id.
        Пример: GET /products/{product_id}
        """
        url = self._url(f"products/{product_id}")
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def search_products(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Поиск товаров по запросу.
        Пример: GET /products/search?q=<query>&limit=<limit>
        """
        url = self._url("products/search")
        resp = self.session.get(url, params={"q": query, "limit": limit})
        resp.raise_for_status()
        data = resp.json()
        # Ожидаем либо список товаров, либо словарь с ключом 'products'
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("products", data.get("items", []))
        return []

    def add_to_cart(self, product_id: str, quantity: int = 1) -> Dict:
        """
        Добавить товар в корзину.
        Пример: POST /cart/add с JSON {'product_id': ..., 'quantity': ...}
        """
        url = self._url("cart/add")
        body = {"product_id": product_id, "quantity": quantity}
        resp = self.session.post(url, json=body)
        resp.raise_for_status()
        return resp.json()

    def get_cart(self) -> Dict:
        """
        Получить текущее содержимое корзины.
        Пример: GET /cart
        """
        url = self._url("cart")
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()

    def remove_from_cart(self, item_id: str) -> Dict:
        """
        Удалить позицию из корзины по id.
        Пример: POST /cart/remove с JSON {'item_id': ...}
        """
        url = self._url("cart/remove")
        resp = self.session.post(url, json={"item_id": item_id})
        resp.raise_for_status()
        return resp.json()