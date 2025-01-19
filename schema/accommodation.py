from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class DiscountType(str, Enum):
    CHILD_UNDER_6 = "children under 6 years of age"
    CHILD_6_TO_12 = "children from 6 to 12 years of age"
    TRAVEL_COMPANY = "organized through a travel company"
    STAFF_RELATIVE = "relatives of hotel staff members"

class RoomType(str, Enum):
    SINGLE = "Single"
    TWIN = "Twin"
    APARTMENT = "Apartment"

class Discount(BaseModel):
    discount_type: DiscountType = Field(..., description="The amount for discount, range from 0 to 100 percentages")
    discount_reason: float = Field(..., description="The reason for discount")
    
class RoomDetail(BaseModel):
    amounts: int = Field(..., description="Number of rooms the customer group wants to book")
    room_type: RoomType = Field(..., description="The type of rooms the customer group wants to book")
    discount_list: t.List[Discount] = Field(..., description="The list of discount, if not discount specify, leave this empty")

class DayAccommodationDetail(BaseModel):
    index: int = Field(..., description="The index base on the order of trip")
    room_details: t.List[RoomDetail] = Field(..., description="Description of the types of rooms the customer wants to book, there can be different type of room customes want to book")
    breakfast: float = Field(..., description="Customer choice for breakfast: 1 for yes and 0 for none")

class TripAccommodationDetail(BaseModel):
    day_accommodation: t.List[DayAccommodationDetail] = Field(..., description="The detail of acommodation in each days, the last day will don't have any acommodation")