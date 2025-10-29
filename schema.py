from pydantic import BaseModel

from datetime import datetime, timezone  # noqa


class CountriesBase(BaseModel):
    name: str
    capital: str | None = None
    region: str | None = None
    population: int
    currency_code: str | None
    exchange_rate: float | None
    estimated_gdp: float | None
    flag_url: str | None = None
    last_refreshed_at: datetime | None


class Country(BaseModel):
    id: int
    name: str
    capital: str | None = None
    region: str | None = None
    population: int
    currency_code: str | None
    exchange_rate: float | None
    estimated_gdp: float | None
    flag_url: str | None = None
    last_refreshed_at: datetime | None
