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
        description="The time participants want to use the meal (hour and minute only). If not specified, leave as null."
    )
    meal_name: t.Optional[str] = Field(
        ...,
        description="The name of the meal in the menu. If the type meal is Breakfast or Winery or the name is not specify, leave as null."
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