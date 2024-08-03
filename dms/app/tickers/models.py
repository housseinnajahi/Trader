from sqlalchemy import BigInteger, Boolean, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import class_mapper, mapped_column, relationship

from ..postgres import postgres

TICKERS = "tickers"
AGGREGATIONS = "aggregations"


class Ticker(postgres.base):
    __tablename__ = TICKERS

    id = mapped_column(Integer, primary_key=True, index=True)
    ticker = mapped_column(String, unique=True)
    name = mapped_column(String, nullable=True)
    market = mapped_column(String, nullable=True)
    locale = mapped_column(String, nullable=True)
    type = mapped_column(String, nullable=True)
    active = mapped_column(Boolean, default=True)
    currency_name = mapped_column(String, nullable=True)
    composite_figi = mapped_column(String, nullable=True)
    share_class_figi = mapped_column(String, nullable=True)
    last_updated_utc = mapped_column(String, nullable=True)
    aggregations = relationship(
        "Aggregation",
        back_populates="ticker",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self):
        return f"<Ticker(id={self.id}, ticker={self.ticker}, name={self.name}, is_active={self.active})>"

    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns
        }


class Aggregation(postgres.base):
    __tablename__ = AGGREGATIONS
    id = mapped_column(Integer, primary_key=True, index=True)
    close_price = mapped_column(Float)
    highest_price = mapped_column(Float)
    lowest_price = mapped_column(Float)
    number_of_transactions = mapped_column(Integer)
    open_price = mapped_column(Float)
    timestamp = mapped_column(BigInteger)
    trading_volume = mapped_column(Float)
    volume_weighted_average_price = mapped_column(Float)
    from_date = mapped_column(Date)
    to_date = mapped_column(Date)
    ticker_id = mapped_column(Integer, ForeignKey(f"{TICKERS}.id"))
    ticker = relationship("Ticker", back_populates="aggregations")

    def __repr__(self):
        return f"<Aggregation(id={self.id}, ticker={self.ticker_id}, timestamp={self.timestamp})>"

    def to_dict(self):
        return {
            c.key: getattr(self, c.key) for c in class_mapper(self.__class__).columns
        }