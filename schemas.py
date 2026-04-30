from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from models import Coordinates


class StudentsScope(str, Enum):
    MY_CLASS = "my_class"
    ALL_STUDENTS = "all_students"
    ALL_TEACHERS = "all_teachers"


class RegisterRequest(BaseModel):
    user_id: int
    name: str
    class_name: str
    role: str
    password: str


class LoginRequest(BaseModel):
    user_id: int
    password: str


class UpdateLocationRequest(BaseModel):
    model_config = {"populate_by_name": True}

    user_id: int = Field(alias="ID")
    coordinates: Coordinates = Field(alias="Coordinates")
    time: datetime = Field(alias="Time")
