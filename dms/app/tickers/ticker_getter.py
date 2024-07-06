from datetime import datetime, timedelta

from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session

from ..exceptions.exceptions import TickerNotFoundException
from ..redis import redis_client
from ..tickers import models
from ..tickers.schemas import Ticker


class TickerGetter:
    @classmethod
    def get_ticker_by_id(cls, ticker_id: int, db: Session) -> Ticker:
        ticker: Ticker = (
            db.query(models.Ticker).filter(models.Ticker.id == ticker_id).first()
        )
        if ticker:
            return ticker
        raise TickerNotFoundException(ticker_id=str(ticker_id))

    @classmethod
    def get_ticker_by_symbol(cls, ticker_symbol: str, db: Session) -> Ticker:
        ticker: Ticker = (
            db.query(models.Ticker)
            .filter(models.Ticker.ticker == ticker_symbol)
            .first()
        )
        if ticker:
            return ticker
        raise TickerNotFoundException(
            ticker_id=ticker_symbol, msg=f"Ticker {ticker_symbol} is not found"
        )

    @classmethod
    def get_tickers(cls, limit: int, offset: int, db: Session) -> list[Ticker]:
        if limit == -1:
            tickers: list[Ticker] = db.query(models.Ticker).all()
        else:
            tickers: list[Ticker] = db.query(models.Ticker).limit(limit).offset(offset)
        return tickers

    @classmethod
    def get_ticker_without_aggregation(cls, db: Session) -> tuple:
        target_date = datetime.now().date() - timedelta(days=1)
        computed_aggregations = redis_client.get_computed_aggregations(
            key="computed_aggregations"
        )
        tickers_without_aggs: list[str] = [ticker for ticker in computed_aggregations]

        # Subquery to get ticker IDs that have an aggregation for the target date
        subquery = (
            db.query(models.Aggregation.ticker_id)
            .filter(models.Aggregation.to_date == target_date)
            .subquery()
        )

        # Query to find the first ticker without aggregation on the target date or with no aggregations at all
        ticker = (
            db.query(
                models.Ticker.id,
                models.Ticker.ticker,
                func.max(models.Aggregation.to_date).label("latest_to_date"),
            )
            .outerjoin(
                models.Aggregation,
                and_(models.Ticker.id == models.Aggregation.ticker_id),
            )
            .filter(
                and_(
                    or_(
                        models.Aggregation.ticker_id == None,
                        ~models.Ticker.id.in_(subquery),
                    ),
                    ~models.Ticker.ticker.in_(tickers_without_aggs),
                )
            )
            .group_by(models.Ticker.id)
            .order_by(models.Ticker.id)
            .first()
        )
        if ticker:
            return ticker[0], ticker[1], ticker[2]
        else:
            return None, None, None


ticker_getter = TickerGetter()
