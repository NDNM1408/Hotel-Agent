from datetime import datetime
from pydantic import BaseModel, Field
import typing as t
class DayDetail(BaseModel):
    index: int = Field(..., description="Order of day")
    day_time: datetime = Field(..., description="The date of the day")
    description: str = Field(..., description="Description about every service the group of customer using in that day")

class TripDetail(BaseModel):
    guest_amounts: int = Field(..., description="The amount of guest at the beginning of the trip")
    number_of_day: int = Field(..., description="The number of days of the trip")
    start_date: datetime = Field(..., description="The start date of the trip")
    details: t.List[DayDetail] = Field(..., description="The detail of each day of the trip")