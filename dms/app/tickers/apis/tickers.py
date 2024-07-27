from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.openapi.models import Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ...elasticsearch import es_client
from ...exceptions.exceptions import catch_errors
from ...postgres import postgres
from ..models import TICKERS
from ..schemas import Aggregation, Ticker, TickerCreate, TickerUpdate
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


@router.get("/{symbol}/aggregations/{start_date}/{end_date}")
@catch_errors
def get_ticker_aggregations(
    symbol: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(postgres.get_db),
) -> list[Aggregation]:
    return ticker_service.get_ticker_aggregations(
        ticker=symbol, start_date=start_date, end_date=end_date, db=db
    )


@router.get("/{symbol}/aggregations/{start_date}/{end_date}/export")
@catch_errors
def export_ticker_aggregations(
    symbol: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(postgres.get_db),
):
    csv_content = ticker_service.export_ticker_aggregations(
        ticker=symbol, start_date=start_date, end_date=end_date, db=db
    )
    response = StreamingResponse(csv_content, media_type="text/csv")
    response.headers["Content-Disposition"] = (
        f"attachment; filename=aggregations_of_{symbol}_from_{start_date}_to_{end_date}.csv"
    )
    return response
