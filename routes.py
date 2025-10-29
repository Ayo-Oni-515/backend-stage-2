import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlmodel import Session

from utils import get_session
from services import CountryService
from exceptions import (
    CountryDataAPIError,
    ExchangeRateAPIError,
    ImageGenerationError)
from schema import Country

countries_router = APIRouter(prefix="/countries")


@countries_router.get(
        "/image",
        status_code=status.HTTP_200_OK)
async def serve_summary_image():
    summary = os.listdir("./cache")

    if "summary.png" not in summary:
        raise HTTPException(
            status_code=404,
            detail={"error": "Summary image not found"}
        )

    return FileResponse(
        path="cache/summary.png",
        media_type="image/png",
        filename="summary.png"
    )


@countries_router.post("/refresh",
                       status_code=status.HTTP_200_OK)
async def fetch_all_countries_and_cache(
        session: Session = Depends(get_session)):
    try:
        CountryService.refresh(session=session)

        total_countries, timestamp = CountryService.get_country_status(
            session=session
        )

        top_gdp_countries = (CountryService.gdp_sort(
            sort_by="gdp_desc",
            session=session
        ))[:5]

        CountryService.generate_country_image(
            total_countries=total_countries,
            last_refreshed_at=timestamp.last_refreshed_at,
            top_gdp_countries=top_gdp_countries
        )
    except CountryDataAPIError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not fetch data from Country Data API"
        )
    except ExchangeRateAPIError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not fetch data from Exchange Rate API"
        )
    except ImageGenerationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Summary Image could not be generated"
        )


@countries_router.get(
        "",
        status_code=status.HTTP_200_OK,
        response_model=list[Country])
async def get_all_countries(region: Optional[str] = None,
                            currency: Optional[str] = None,
                            sort: Optional[str] = None,
                            session: Session = Depends(get_session)):

    all_countries = CountryService.get_countries(session=session)

    if (
            (region is None) and
            (currency is None) and
            (sort is None)):
        return all_countries

    if region:
        region = region.title()
        return CountryService.get_country_by_region(
            region=region,
            session=session
            )

    if currency:
        currency = currency.upper()
        return CountryService.get_country_by_currency(
            currency_code=currency,
            session=session
        )

    if sort:
        sort = sort.lower()
        try:
            return CountryService.gdp_sort(
                sort_by=sort,
                session=session
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid sort value: must be 'gdp_asc' or 'gdp_desc'"
            )


@countries_router.get(
        "/{name}",
        status_code=status.HTTP_200_OK,
        response_model=Country)
async def get_country_by_name(
        name: str,
        session: Session = Depends(get_session)):
    try:
        name = name.lower()
        country = CountryService.get_country_name(
            country_name=name,
            session=session
        )

        if not country:
            raise ValueError

        return country
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )


@countries_router.delete(
        "/{name}",
        status_code=status.HTTP_204_NO_CONTENT)
async def delete_a_country_record(
        name: str,
        session: Session = Depends(get_session)):
    try:
        name = name.lower()
        CountryService.delete_country_name(
            country_name=name,
            session=session
        )

        return
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found"
        )
