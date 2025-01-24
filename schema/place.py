from datetime import time
from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class Utility(str, Enum):
    CINEMA = "Cinema"
    SCHOOL = "School"
    DINNER = "Dinner"
    BOARDROOM = "Boardroom"
    UTABLE = "U-Table"
    PARTY = "Party"

class Place(BaseModel):
    place: t.Optional[str] = Field(
        None,
        description="The place that guests rent in their trip"
    )
    utilities: t.List[Utility] = Field(
        ...,
        description="The list of utilities that guests rent in their trip"
    )
    full_day: bool = Field(
        ...,
        description="Whether guests hire the place full day or not, based on the time they hire"
    )

class RentPlaces(BaseModel):
    rent_utilities: t.List[Place] = Field(
        ...,
        description="The list of utilities that customers rent based on the description"
    )
