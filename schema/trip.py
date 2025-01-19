from datetime import datetime
from pydantic import BaseModel, Field
import typing as t

class DayDetail(BaseModel):
    index: int = Field(..., description="Order of day")
    day_time: t.Optional[datetime] = Field(..., description="The date of the day")
    description: t.Optional[str] = Field(..., description="Description about every service the group of customer using in that day, if no description too detail leave null")

class TripDetail(BaseModel):
    guest_amounts: t.Optional[int] = Field(..., description="The amount of guest at the beginning of the trip, if not specify leave null don't guess")
    number_of_day: t.Optional[int] = Field(..., description="The number of days of the trip, if not specify leave null don't guess")
    start_date: t.Optional[datetime] = Field(..., description="The start date of the trip, if not specify leave null don't guess")
    details: t.List[DayDetail] = Field(..., description="The detail of each day of the trip")