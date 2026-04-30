from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import BaseModel, Field


class DMS(BaseModel):
    model_config = {"populate_by_name": True}

    degrees: int = Field(alias="Degrees")
    minutes: int = Field(alias="Minutes")
    seconds: int = Field(alias="Seconds")


class Coordinates(BaseModel):
    model_config = {"populate_by_name": True}

    longitude: DMS = Field(alias="Longitude")
    latitude: DMS = Field(alias="Latitude")


class Location(BaseModel):
    model_config = {"populate_by_name": True}

    coordinates: Coordinates = Field(alias="Coordinates")
    time: datetime = Field(alias="Time")


class User(Document):
    user_id: int
    name: str
    class_name: str
    role: str
    password: str
    token: Optional[str] = None
    location: Optional[Location] = None

    class Settings:
        name = "users"
