import logging
from typing import Optional, Union

from elasticsearch import Elasticsearch
from sqlalchemy.orm import Session

from .settings.elasticsearch_settings import elasticsearch_settings
from .tickers.models import TICKERS
from .tickers.schemas import Ticker
from .tickers.ticker_getter import ticker_getter

logger = logging.getLogger("uvicorn")

SEARCH_FIELDS = {
    TICKERS: {
        "ticker": 3,
        "name": 3,
        "composite_figi": 1,
        "share_class_figi": 1,
    }
}


class ElasticsearchClient:
    def __init__(self):
        self.es = Elasticsearch(
            [
                {
                    "host": elasticsearch_settings.ELASTICSEARCH_HOST,
                    "port": elasticsearch_settings.ELASTICSEARCH_PORT,
                    "use_ssl": False,
                }
            ]
        )

    def es_index(self, index: str, element: Union[Ticker]):
        logger.info(f"indexing {index}")
        self.es.index(index=index, id=element.id, body=element.to_dict())

    def es_search(self, query: str, index: str):
        wildcard_queries = [
            {"wildcard": {field: {"value": f"*{query}*", "boost": weight}}}
            for field, weight in SEARCH_FIELDS[index].items()
        ]

        search_body = {
            "query": {"bool": {"should": wildcard_queries, "minimum_should_match": 1}}
        }
        res = self.es.search(index=index, body=search_body)
        return [hit["_source"] for hit in res["hits"]["hits"]]

    def es_delete(self, index: str, id: int):
        self.es.delete(index=index, id=id)

    def reindex_all(self, index: str, db: Session):
        items = []
        if index == TICKERS:
            items = ticker_getter.get_tickers(limit=-1, offset=0, db=db)

        logger.info(f"indexing {index}")
        for item in items:
            self.es_index(index=index, element=item)
        logger.info(f"finished indexing {index}")


es_client = ElasticsearchClient()
