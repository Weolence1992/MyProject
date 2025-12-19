import requests
import logging
from typing import Optional, Dict, Any
import json

logger = logging.getLogger(__name__)


class PetStoreAPIClient:
    """Клиент для работы с API PetStore"""

    def __init__(self, base_url: str = "https://petstore.swagger.io/v2"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Выполнить HTTP запрос"""
        url = f"{self.base_url}{endpoint}"

        logger.debug(f"Making {method} request to {url}")

        try:
            response = self.session.request(method=method, url=url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """GET запрос"""
        return self.make_request("GET", endpoint, params=params)

    def post(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """POST запрос"""
        json_data = json.dumps(data) if data else None
        return self.make_request("POST", endpoint, data=json_data)

    def put(self, endpoint: str, data: Optional[Dict] = None) -> requests.Response:
        """PUT запрос"""
        json_data = json.dumps(data) if data else None
        return self.make_request("PUT", endpoint, data=json_data)

    def delete(self, endpoint: str) -> requests.Response:
        """DELETE запрос"""
        return self.make_request("DELETE", endpoint)