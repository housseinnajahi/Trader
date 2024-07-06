from sqlalchemy.orm import Session

from ..elasticsearch import es_client
from ..exceptions.exceptions import TickerNotFoundException
from ..tickers import models
from ..tickers.schemas import (
    Aggregation,
    AggregationCreate,
    Ticker,
    TickerCreate,
    TickerUpdate,
)
from .models import TICKERS


class TickerSetter:
    @classmethod
    def create_ticker(cls, ticker: TickerCreate, db: Session) -> Ticker:
        db_ticker = models.Ticker(**ticker.dict())
        db.add(db_ticker)
        db.commit()
        db.refresh(db_ticker)
        es_client.es_index(index=TICKERS, element=db_ticker)
        return db_ticker

    @classmethod
    def update_ticker(cls, ticker_id: int, ticker: TickerUpdate, db: Session):
        db_ticker = (
            db.query(models.Ticker).filter(models.Ticker.id == ticker_id).first()
        )
        if db_ticker:
            for key, value in ticker.dict().items():
                setattr(db_ticker, key, value)
            db.commit()
            db.refresh(db_ticker)
            es_client.es_index(index=TICKERS, element=db_ticker)
            return db_ticker
        raise TickerNotFoundException(ticker_id=str(ticker_id))

    @classmethod
    def delete_ticker(cls, ticker_id: int, db: Session):
        db_ticker = (
            db.query(models.Ticker).filter(models.Ticker.id == ticker_id).first()
        )
        if db_ticker:
            db.delete(db_ticker)
            db.commit()
            es_client.es_delete(index=TICKERS, id=ticker_id)
            return db_ticker
        raise TickerNotFoundException(ticker_id=str(ticker_id))

    @classmethod
    def create_aggregation(
        cls, aggregation: AggregationCreate, db: Session
    ) -> Aggregation:
        db_aggregation = models.Aggregation(**aggregation.dict())
        db.add(db_aggregation)
        db.commit()
        db.refresh(db_aggregation)
        return db_aggregation


ticker_setter = TickerSetter()
