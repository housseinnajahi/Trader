from functools import wraps
from typing import Optional

from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError, SQLAlchemyError


class TickerNotFoundException(Exception):
    def __init__(self, ticker_id: str, msg: Optional[str] = None):
        self.ticker_id = ticker_id
        super().__init__()
        if msg:
            self.message = msg
        else:
            self.message = f"Ticker with ID {ticker_id} is not found"
        super().__init__(self.message)


def catch_errors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e))
        except TickerNotFoundException as e:
            print(f"Caught RoleNotFoundException: {e}")
            raise HTTPException(status_code=404, detail=str(e))
        except IntegrityError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Ticker creation failed: This ticker already exists. {str(e)}",
            )
        except SQLAlchemyError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Ticker creation failed: An error occurred while inserting the Ticker. {str(e)}",
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    return wrapper
