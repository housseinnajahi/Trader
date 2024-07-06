from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.openapi.models import Response
from sqlalchemy.orm import Session

from ...elasticsearch import es_client
from ...exceptions.exceptions import catch_errors
from ...postgres import postgres
from ..models import TICKERS
from ..schemas import Ticker, TickerCreate, TickerUpdate
from ..services import ticker_service

router = APIRouter(prefix="")


@router.get("")
@catch_errors
def get_tickers(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(postgres.get_db),
) -> list[Ticker]:
    return ticker_service.get_tickers(limit=limit, offset=offset, db=db)


@router.get("/{ticker_id}")
@catch_errors
def get_ticker_by_id(
    ticker_id: int,
    db: Session = Depends(postgres.get_db),
) -> Ticker:
    return ticker_service.get_ticker_by_id(ticker_id=ticker_id, db=db)


@router.get("/symbol/{symbol}")
@catch_errors
def get_ticker_by_id(
    symbol: str,
    db: Session = Depends(postgres.get_db),
) -> Ticker:
    return ticker_service.get_ticker_by_symbol(ticker=symbol, db=db)


@router.post("")
@catch_errors
def create_ticker(
    ticker: TickerCreate,
    db: Session = Depends(postgres.get_db),
) -> Ticker:
    return ticker_service.create_ticker(ticker=ticker, db=db)


@router.put("/{ticker_id}")
@catch_errors
def update_ticker(
    ticker_id: int,
    ticker: TickerUpdate,
    db: Session = Depends(postgres.get_db),
) -> Ticker:
    return ticker_service.update_ticker(ticker_id=ticker_id, ticker=ticker, db=db)


@router.delete("/{ticker_id}")
@catch_errors
def delete_ticker(
    ticker_id: int,
    db: Session = Depends(postgres.get_db),
) -> Ticker:
    return ticker_service.delete_ticker(ticker_id=ticker_id, db=db)


@router.post("/reindex")
@catch_errors
def reindex_tickers(
    db: Session = Depends(postgres.get_db),
):
    return es_client.reindex_all(index=TICKERS, db=db)


@router.get("/search/{query}")
@catch_errors
def search_tickers(
    query: str,
) -> list[Ticker]:
    return es_client.es_search(query=query, index=TICKERS)
