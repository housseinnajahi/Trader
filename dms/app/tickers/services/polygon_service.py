import datetime
import json
import logging
from typing import Optional

import requests
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from ...postgres import postgres
from ...redis import redis_client
from ...settings.polygon_settings import polygon_settings
from ..schemas import AggregationCreate, TickerCreate
from ..ticker_getter import ticker_getter
from . import ticker_service

logger = logging.getLogger("uvicorn")
STARTING_DATE = "2024-01-01"
MIGRATION_DATE = "2024-06-01"
TIMELAPSE_CONFIG = {
    MIGRATION_DATE: {
        "timespan": "minute",
        "multiplier": 10,
        "duration": 10,
    },
    "default": {
        "timespan": "minute",
        "multiplier": 10,
        "duration": 0,
    },
}


class PolygonClient:
    def __init__(self):
        self.headers: dict = {
            "Authorization": f"Bearer {polygon_settings.POLYGON_API_KEY}"
        }
        self.api_url: str = polygon_settings.POLYGON_API_URL

    def get_tickers(
        self,
        limit: int = 1000,
    ):
        url: str = redis_client.get("next_tickers_url")
        if not url:
            url = f"{self.api_url}v3/reference/tickers?limit={limit}"
        last_tickers_url: str = redis_client.get("last_tickers_url")
        if last_tickers_url:
            return
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response = response.json()
            db: Session = postgres.sessionLocal()

            output = {
                "success": [],
                "fails": [],
            }
            for result in response["results"]:
                ticker: TickerCreate = TickerCreate(**result)
                try:
                    ticker_service.create_ticker(ticker=ticker, db=db)
                    output["success"].append({"ticker": ticker.ticker})
                except IntegrityError as e:
                    output["fails"].append(
                        {
                            "ticker": ticker.ticker,
                            "message": f"Ticker creation failed: This ticker already exists. {str(e)}",
                        }
                    )
                except SQLAlchemyError as e:
                    output["fails"].append(
                        {
                            "ticker": ticker.ticker,
                            "message": f"Ticker creation failed: An error occurred while inserting the Ticker. {str(e)}",
                        }
                    )
            logger.info(json.dumps(output, indent=4))
            if response["count"] < limit:
                redis_client.set("last_tickers_url", "true", 36000)
            redis_client.set("next_tickers_url", response["next_url"])

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")

    def get_aggregations(
        self,
    ):
        db: Session = postgres.sessionLocal()
        params = self.generate_request_params(db=db)
        if params is None:
            return
        url: str = (
            f"{self.api_url}v2/aggs/ticker/{params['ticker']}/range/{params['multiplier']}/{params['timespan']}/{params['from_date']}/{params['to_date']}?adjusted=true&sort=asc"
        )
        print(url)
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            response = response.json()
            db: Session = postgres.sessionLocal()
            output = {
                "success": [],
                "fails": [],
            }
            if response["resultsCount"] > 0:
                for result in response["results"]:
                    aggregation: AggregationCreate = AggregationCreate(
                        **{
                            "close_price": result.get("c", 0),
                            "highest_price": result.get("h", 0),
                            "lowest_price": result.get("l", 0),
                            "number_of_transactions": result.get("n", 0),
                            "open_price": result.get("o", 0),
                            "timestamp": result.get("t", 0) // 1000,
                            "trading_volume": result.get("v", 0),
                            "volume_weighted_average_price": result.get("vw", 0),
                            "from_date": params["from_date"],
                            "to_date": params["to_date"],
                            "ticker_id": params["ticker_id"],
                        }
                    )
                    try:
                        ticker_service.create_aggregation(
                            aggregation=aggregation, db=db
                        )
                        output["success"].append({"ticker": aggregation.ticker_id})
                    except IntegrityError as e:
                        output["fails"].append(
                            {
                                "aggregation": aggregation.ticker_id,
                                "message": f"Aggregation creation failed: This Aggregation already exists. {str(e)}",
                            }
                        )
                    except SQLAlchemyError as e:
                        output["fails"].append(
                            {
                                "aggregation": aggregation.ticker_id,
                                "message": f"Aggregation creation failed: An error occurred while inserting the Aggregation. {str(e)}",
                            }
                        )
            else:
                redis_client.add_to_list(
                    key="ticker_without_aggs", element=params["ticker"]
                )
            computed_aggregations = redis_client.get_computed_aggregations(
                key="computed_aggregations"
            )
            computed_aggregations[params["ticker"]] = f'{params["to_date"]}'
            redis_client.set_computed_aggregations(
                key="computed_aggregations", computed_aggregations=computed_aggregations
            )
            logger.info(json.dumps(output, indent=4))

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")

    def generate_request_params(self, db: Session) -> Optional[dict]:
        format = "%Y-%m-%d"
        computed_aggregations = redis_client.get_computed_aggregations(
            key="computed_aggregations"
        )
        ticker_id, ticker, date = None, None, None
        for ticker_symbol in computed_aggregations:
            date = datetime.datetime.strptime(
                computed_aggregations[ticker_symbol], format
            ).date()
            if date < datetime.datetime.now().date() - datetime.timedelta(days=1):
                ticker = ticker_getter.get_ticker_by_symbol(
                    ticker_symbol=ticker_symbol, db=db
                )
                ticker_id = ticker.id
                ticker = ticker.ticker
                break
            date = None
        if ticker is None and ticker_id is None and date is None:
            ticker_id, ticker, date = ticker_getter.get_ticker_without_aggregation(
                db=db
            )
        if ticker is None:
            return None
        from_date = (
            date if date else datetime.datetime.strptime(STARTING_DATE, format).date()
        )
        if from_date < datetime.datetime.strptime(MIGRATION_DATE, format).date():
            config_key = MIGRATION_DATE
        else:
            config_key = "default"
            from_date = from_date + datetime.timedelta(days=1)

        return {
            "ticker_id": ticker_id,
            "ticker": ticker,
            "from_date": from_date,
            "to_date": from_date
            + datetime.timedelta(days=TIMELAPSE_CONFIG[config_key]["duration"]),
            "timespan": TIMELAPSE_CONFIG[config_key]["timespan"],
            "multiplier": TIMELAPSE_CONFIG[config_key]["multiplier"],
        }

    @staticmethod
    def format_scientific_float(num: float) -> float:
        num_str = str(num)
        if "e" in num_str or "E" in num_str:
            regular_float_str = "{:.12f}".format(num)
            return float(regular_float_str)
        return num


polygon_client = PolygonClient()
