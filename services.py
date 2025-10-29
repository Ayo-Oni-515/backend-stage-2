from datetime import datetime, timezone
import os
from random import randrange
from typing import Literal

import requests
from dotenv import load_dotenv
from sqlmodel import Session, select
from PIL import Image, ImageDraw, ImageFont

from schema import CountriesBase
from models import Countries
from exceptions import (
    CountryDataAPIError,
    ExchangeRateAPIError,
    ImageGenerationError)


load_dotenv()


COUNTRY_DATA_API = os.getenv("COUNTRY_DATA_API")
EXCHANGE_RATE_API = os.getenv("EXCHANGE_RATE_API")


class CountryService():
    @staticmethod
    def extract_data(country_data: list, exchange_rates: dict) -> list:
        all_countries = []

        for data in country_data:

            # when currency array is not empty
            if len(data.get("currencies", {})) >= 1:

                if (
                    data["currencies"][0]["code"]
                ) not in exchange_rates.keys():
                    # when the exchange rate is not available
                    currency_code = data["currencies"][0]["code"]
                    exchange_rate = None
                    estimated_gdp = None

                else:
                    # when the exchange rate is available
                    currency_code = data["currencies"][0]["code"]
                    exchange_rate = exchange_rates[currency_code]
                    estimated_gdp = round((
                        data["population"] * (
                            randrange(1000, 2000))) / exchange_rate, 2)

            else:
                # when currency array is empty
                currency_code = None
                exchange_rate = None
                estimated_gdp = 0

            country = CountriesBase(
                name=data.get("name"),
                capital=data.get("capital", None),
                region=data.get("region", None),
                population=data["population"],
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                estimated_gdp=estimated_gdp,
                flag_url=data.get("flag", None),
                last_refreshed_at=None  # so global timestamp are the same
            )

            all_countries.append(country.model_dump())

        return all_countries

    @staticmethod
    def refresh(session: Session):
        # check db table
        db_data: list = CountryService.get_countries(session)

        try:
            # fetch country api
            country_data = requests.get(
                url=COUNTRY_DATA_API,
                timeout=30.0
            ).json()
        except Exception:
            raise CountryDataAPIError

        try:
            # fetch exchange rates api
            exchange_rates = (requests.get(
                url=EXCHANGE_RATE_API,
                timeout=30.0
            ).json())["rates"]
        except Exception:
            raise ExchangeRateAPIError

        refreshed = CountryService.extract_data(
            country_data=country_data,
            exchange_rates=exchange_rates)

        last_refreshed_at = datetime.now(timezone.utc)

        if len(db_data) == 0:
            # for an empty table (insertion)
            for data in refreshed:
                country = Countries(
                    name=(data["name"]).lower(),
                    capital=data["capital"],
                    region=data["region"],
                    population=data["population"],
                    currency_code=data["currency_code"],
                    exchange_rate=data["exchange_rate"],
                    estimated_gdp=data["estimated_gdp"],
                    flag_url=data["flag_url"],
                    last_refreshed_at=last_refreshed_at
                )

                try:
                    session.add(country)
                    session.commit()
                    session.refresh(country)
                except Exception:
                    session.rollback()
        else:
            # for a filled table (updating)
            for data in refreshed:
                country_name = (data["name"]).lower()
                country = CountryService.get_country_name(
                    country_name=country_name,
                    session=session)

                if country is None:
                    # if the country has been deleted
                    country = Countries(
                        name=(data["name"]).lower(),
                        capital=data["capital"],
                        region=data["region"],
                        population=data["population"],
                        currency_code=data["currency_code"],
                        exchange_rate=data["exchange_rate"],
                        estimated_gdp=data["estimated_gdp"],
                        flag_url=data["flag_url"],
                        last_refreshed_at=last_refreshed_at
                    )
                elif country:
                    # if the country is already present
                    country.capital = data["capital"]
                    country.region = data["region"]
                    country.population = data["population"]
                    country.currency_code = data["currency_code"]
                    country.exchange_rate = data["exchange_rate"]
                    country.estimated_gdp = data["estimated_gdp"]
                    country.flag_url = data["flag_url"]
                    country.last_refreshed_at = last_refreshed_at

                try:
                    session.add(country)
                    session.commit()
                    session.refresh(country)
                except Exception:
                    session.rollback()

    @staticmethod
    def get_countries(session: Session):
        sql_query = select(Countries)
        query_result = session.exec(sql_query).all()

        return query_result

    @staticmethod
    def get_country_name(country_name: str, session: Session):
        sql_query = select(Countries).where(Countries.name == country_name)
        query_result = session.exec(sql_query).first()

        return query_result

    @staticmethod
    def get_country_by_region(region: str, session: Session):
        sql_query = select(Countries).where(Countries.region == region)
        query_result = session.exec(sql_query).all()

        return query_result

    @staticmethod
    def get_country_by_currency(currency_code: str, session: Session):
        sql_query = select(Countries).where(
            Countries.currency_code == currency_code)
        query_result = session.exec(sql_query).all()

        return query_result

    def gdp_sort(sort_by: Literal["gdp_asc", "gdp_desc"], session: Session):
        if sort_by == "gdp_asc":
            sql_query = select(Countries).order_by(
                Countries.estimated_gdp.asc())
            query_result = session.exec(sql_query).all()
        elif sort_by == "gdp_desc":
            sql_query = select(Countries).order_by(
                Countries.estimated_gdp.desc())
            query_result = session.exec(sql_query).all()

        return query_result

    @staticmethod
    def delete_country_name(country_name: str, session: Session):
        country = CountryService.get_country_name(
            country_name=country_name,
            session=session)

        if not country:
            raise ValueError

        session.delete(country)
        session.commit()

    @staticmethod
    def get_country_status(session: Session):
        count = len(CountryService.get_countries(session=session))
        last_refreshed_at = session.exec(
            select(Countries).where(Countries.last_refreshed_at)).first()

        return (count, last_refreshed_at)

    @staticmethod
    def generate_country_image(
            total_countries: str,
            last_refreshed_at,
            top_gdp_countries,
            output_path="cache/summary.png"):

        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Image dimensions
            width = 800
            height = 600

            # Colors
            bg_color = (255, 255, 255)  # White background
            primary_color = (41, 128, 185)  # Blue
            text_color = (44, 62, 80)  # Dark gray
            # accent_color = (52, 152, 219)  # Light blue

            # Create image
            img = Image.new('RGB', (width, height), bg_color)
            draw = ImageDraw.Draw(img)

            title_font = ImageFont.load_default()
            heading_font = ImageFont.load_default()
            body_font = ImageFont.load_default()

            # Draw header bar
            draw.rectangle([0, 0, width, 80], fill=primary_color)

            # Title
            title = "HNG 13: Country Data Summary"
            title_bbox = draw.textbbox((0, 0), title, font=title_font)
            title_width = title_bbox[2] - title_bbox[0]
            draw.text(
                ((width - title_width) // 2, 22), title, fill=(
                    255, 255, 255), font=title_font)

            # Last refresh section
            y_offset = 120
            draw.text(
                (50, y_offset),
                "Last Refreshed:", fill=primary_color, font=heading_font)
            y_offset += 30
            draw.text(
                (50, y_offset),
                str(last_refreshed_at), fill=text_color, font=body_font)

            # Total countries section
            y_offset += 60
            draw.text(
                (50, y_offset),
                "Total Countries:", fill=primary_color, font=heading_font)
            y_offset += 30
            draw.text(
                (50, y_offset),
                str(total_countries), fill=text_color, font=body_font)

            # Top 5 GDP section
            y_offset += 60
            draw.text(
                (50, y_offset),
                "Top 5 Countries by GDP",
                fill=primary_color, font=heading_font)
            y_offset += 40

            for pos, country in enumerate(top_gdp_countries):
                gdp_formatted = f"{pos + 1}. \
{country.name} - {country.estimated_gdp}"

                draw.text(
                    (50, y_offset),
                    gdp_formatted, fill=text_color, font=body_font)

                y_offset += 35

            # Save image
            img.save(output_path, 'PNG')
        except Exception:
            raise ImageGenerationError
