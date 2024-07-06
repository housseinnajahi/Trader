from datetime import date
from typing import Optional

from pydantic import BaseModel


class AggregationBase(BaseModel):
    close_price: float
    highest_price: float
    lowest_price: float
    number_of_transactions: int
    open_price: float
    timestamp: int
    trading_volume: float
    volume_weighted_average_price: float
    from_date: date
    to_date: date
    ticker_id: int


class AggregationCreate(AggregationBase):
    pass


class Aggregation(AggregationBase):
    id: int

    class Config:
        orm_mode = True


class TickerBase(BaseModel):
    ticker: str
    name: Optional[str] = None
    market: Optional[str] = None
    locale: Optional[str] = None
    type: Optional[str] = None
    active: bool
    currency_name: Optional[str] = None
    composite_figi: Optional[str] = None
    share_class_figi: Optional[str] = None
    last_updated_utc: Optional[str] = None


class TickerCreate(TickerBase):
    pass


class TickerUpdate(TickerBase):
    pass


class Ticker(TickerBase):
    id: int
    aggregations: list[Aggregation] = []

    class Config:
        orm_mode = True
