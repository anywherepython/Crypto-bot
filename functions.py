import requests
from .config import CURRENCY_API, CRYPTO_COMPARE_API

def get_currency_rate(currency: str) -> float | None:
    response = requests.get(CURRENCY_API)
    data = response.json()
    if currency.upper() in data["rates"]:
        return data["rates"][currency.upper()]
    return None


def calculate_currency_amount(amount: float, rate: float) -> float:
    return amount * rate


def calculate_crypto_amount(amount: float, crypto_price: float) -> float:
    return amount * crypto_price


def get_crypto_compare_price() -> dict | None:
    response = requests.get(CRYPTO_COMPARE_API)
    if response.status_code == 200:
        return response.json()
    return None
