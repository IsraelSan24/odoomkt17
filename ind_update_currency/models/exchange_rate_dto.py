from dataclasses import dataclass


@dataclass
class ExchangeRateDTO:
    purchase_price: float
    sale_price: float
    currency: str
    date: str
