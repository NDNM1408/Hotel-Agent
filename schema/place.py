from datetime import time
from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class Utility(str, Enum):
    CINEMA = "Cinema"
    SCHOOL = "School"
    DINNER = "Winery"
    BOARDROOM = "Boardroom"
    UTABLE = "U-Table"
    PARTY = "Party"

class Place(BaseModel):
    place: t.Optional[str] = Field(
        ...,
        "The place that guests rent in their trip"
    )
    utilities: t.List[Utility] = Field(
        ...,
        "The list of uilities that guests rent in their trip"
    )
    full_day: bool = Field(
        ...,
        "Whether guests hire the place full day or not, basing on the time they hire"
    )

class RentPlaces(BaseModel):
    rent_utilities: t.List[Place] = Field(
        ...,
        "The list of of utilities that customer renting basing on the description"
    )