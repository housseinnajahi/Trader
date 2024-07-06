from sqlalchemy.orm import Session

from ...tickers.schemas import AggregationCreate, Ticker, TickerCreate, TickerUpdate
from ..ticker_getter import ticker_getter
from ..ticker_setter import ticker_setter


def get_ticker_by_id(ticker_id: int, db: Session) -> Ticker:
    return ticker_getter.get_ticker_by_id(ticker_id=ticker_id, db=db)


def get_ticker_by_symbol(ticker: str, db: Session) -> Ticker:
    return ticker_getter.get_ticker_by_symbol(ticker_symbol=ticker, db=db)


def get_tickers(limit: int, offset: int, db: Session) -> list[Ticker]:
    return ticker_getter.get_tickers(limit=limit, offset=offset, db=db)


def create_ticker(ticker: TickerCreate, db: Session) -> Ticker:
    return ticker_setter.create_ticker(ticker=ticker, db=db)


def update_ticker(ticker_id: int, ticker: TickerUpdate, db: Session) -> Ticker:
    return ticker_setter.update_ticker(ticker_id=ticker_id, ticker=ticker, db=db)


def delete_ticker(ticker_id: int, db: Session) -> Ticker:
    return ticker_setter.delete_ticker(ticker_id=ticker_id, db=db)


def create_aggregation(aggregation: AggregationCreate, db: Session) -> Ticker:
    return ticker_setter.create_aggregation(aggregation=aggregation, db=db)
