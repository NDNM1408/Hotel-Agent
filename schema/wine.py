from datetime import time
from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class WineryMeal(str, Enum):
    WINERY_MEAL_I = "Winery Meal 1"
    WINERY_MEAL_II = "Winery Meal 2"

    

class WineInformation(BaseModel):
    bottle_amounts: t.Optional[int] = Field(
        ...,
        description="Number of bottles guests want to try"
    )
    amount_of_times: t.Optional[int] = Field(
        ...,
        description="Number of hour guest want to rent the winery"
    )
    meals: t.Optional[WineryMeal] = Field(
        ...,
        description="The type of meal at winery guests want to use"
    )

class WineDetail(BaseModel):
    is_winery: bool = Field(..., description="Whether guests using winery services")
    detail: t.Optional[WineInformation] = Field(
        ...,
        description="The information about the wine service they want to use"
    )
    