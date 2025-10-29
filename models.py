from datetime import datetime

from sqlmodel import Field, SQLModel


class Countries(SQLModel, table=True):
    __tablename__ = "countries"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    capital: str | None = Field(default=None)
    region: str | None = Field(default=None)
    population: int
    currency_code: str | None
    exchange_rate: float | None
    estimated_gdp: float | None
    flag_url: str | None
    last_refreshed_at: datetime
