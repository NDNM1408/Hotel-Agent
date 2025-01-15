from datetime import time
from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class MealType(str, Enum):
    BREAKFAST = "Breakfast"
    COFFEE_BREAK = "Coffee Break"
    WINERY = "Winery"
    NORMAL = "Normal"

class MealDetail(BaseModel):
    meal_time: t.Optional[time] = Field(
        None,
        description="The time participants want to use the buffet (hour and minute only). If not specified, leave as null."
    )
    meal_description: str = Field(
        ...,
        description="The description of the buffet based on the customer request."
    )
    meal_type: MealType = Field(
        ...,
        description="The type of the buffet. Must be one of: Breakfast, Coffee Break, Winery, or Normal."
    )

class ListMealDetail(BaseModel):
    buffets: t.List[MealDetail] = Field(
        ...,
        description="List of the meals the customer uses each day. If no meals are specified, leave as an empty list."
    )