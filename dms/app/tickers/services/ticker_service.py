import csv
from io import StringIO

from sqlalchemy.orm import Session

from ...tickers.schemas import (Aggregation, AggregationCreate, Ticker,
                                TickerCreate, TickerUpdate)
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


def get_ticker_aggregations(
    ticker: str, start_date: str, end_date: str, db: Session
) -> list[Aggregation]:
    return ticker_getter.get_ticker_aggregations(
        ticker=ticker, start_date=start_date, end_date=end_date, db=db
    )


def export_ticker_aggregations(
    ticker: str, start_date: str, end_date: str, db: Session
):
    aggregations: list[Aggregation] = ticker_getter.get_ticker_aggregations(
        ticker=ticker, start_date=start_date, end_date=end_date, db=db
    )
    return aggregations_to_csv(aggregations=aggregations)


def aggregations_to_csv(aggregations: list[Aggregation]):
    output = StringIO()
    writer = csv.writer(output)
    fieldnames = [
        field
        for field in Aggregation.__fields__.keys()
        if field not in ["ticker_id", "id"]
    ]
    writer.writerow(fieldnames)
    for aggregation in aggregations:
        writer.writerow([getattr(aggregation, field) for field in fieldnames])

    output.seek(0)
    return output
