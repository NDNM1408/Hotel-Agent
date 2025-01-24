from datetime import datetime
from pydantic import BaseModel, Field
import typing as t
from enum import Enum

class DiscountType(str, Enum):
    CHILD_UNDER_6 = "children under 6 years of age"  # 50%
    CHILD_6_TO_12 = "children from 6 to 12 years of age"  # 15%
    TRAVEL_COMPANY = "organized through a travel company"  # 10%
    STAFF_RELATIVE = "relatives of hotel staff members"  # 15%

class RoomType(str, Enum):
    SINGLE = "Single"
    TWIN = "Twin"
    APARTMENT = "Apartment"

class Discount(BaseModel):
    discount_type: DiscountType = Field(..., description="The type of discount")
    discount_reason: float = Field(..., description="The reason for discount")

class RoomDetail(BaseModel):
    amounts: int = Field(..., description="Number of rooms the customer group wants to book")
    room_type: RoomType = Field(..., description="The type of rooms the customer group wants to book")
    discount_list: t.List[Discount] = Field(..., description="The list of discounts; leave empty if no discounts")

class DayAccommodationDetail(BaseModel):
    index: int = Field(..., description="The index of the day in the trip")
    room_details: t.List[RoomDetail] = Field(..., description="Description of the types of rooms booked")
    breakfast: float = Field(..., description="Customer choice for breakfast: 1 for yes, 0 for none")

class TripAccommodationDetail(BaseModel):
    day_accommodation: t.List[DayAccommodationDetail] = Field(..., description="Accommodation details for each day")

def get_season_and_day_type(date: datetime):
    month = date.month
    day = date.day
    weekday = date.weekday()

    # Determine if it's a normal day or weekend
    day_type = "normal_day" if weekday < 5 else "weekend"

    # Determine the season
    if month in [10, 11, 12, 1, 2, 3]:
        season = "winter"
    elif month in [5, 6, 7, 8, 9]:
        season = "summer"
    elif month == 4:
        season = "spring"


    # Special days override
    if (month == 12 and day == 24) or (month == 12 and day == 31):
        season = "special"

    return season, day_type

def calculate_room_price_with_details(room: RoomDetail, season: str, day_type: str, price_file: dict):
    base_price = price_file[room.room_type.value.lower()][season][day_type]
    total_price = base_price * room.amounts

    formula_parts = [
        f"Base price ({room.room_type.value}, {season}, {day_type}): {base_price}",
        f"Number of rooms: {room.amounts}",
        f"Initial total price: {base_price} x {room.amounts} = {total_price}"
    ]

    # Apply discounts
    for discount in room.discount_list:
        if discount.discount_type == DiscountType.CHILD_UNDER_6:
            discount_value = total_price * 0.5
            total_price *= 0.5  # 50% discount
            formula_parts.append(f"Discount for {discount.discount_type.value}: -50% ({discount_value})")
        elif discount.discount_type == DiscountType.CHILD_6_TO_12:
            discount_value = total_price * 0.15
            total_price *= 0.85  # 15% discount
            formula_parts.append(f"Discount for {discount.discount_type.value}: -15% ({discount_value})")
        elif discount.discount_type == DiscountType.TRAVEL_COMPANY:
            discount_value = total_price * 0.1
            total_price *= 0.9  # 10% discount
            formula_parts.append(f"Discount for {discount.discount_type.value}: -10% ({discount_value})")
        elif discount.discount_type == DiscountType.STAFF_RELATIVE:
            discount_value = total_price * 0.15
            total_price *= 0.85  # 15% discount
            formula_parts.append(f"Discount for {discount.discount_type.value}: -15% ({discount_value})")

    return total_price, formula_parts

def calculate_trip_accommodation(trip: TripAccommodationDetail, start_date: datetime, price_file: dict):
    total_price = 0
    detailed_breakdown = []

    for day_offset, day_accommodation in enumerate(trip.day_accommodation):
        current_date = start_date.replace(day=start_date.day + day_offset)
        season, day_type = get_season_and_day_type(current_date)

        day_total = 0
        day_details = [f"Day {day_accommodation.index} ({current_date.strftime('%Y-%m-%d')}):"]

        for room in day_accommodation.room_details:
            room_price, room_details = calculate_room_price_with_details(room, season, day_type, price_file)
            day_total += room_price
            day_details.extend(room_details)

        if not day_accommodation.breakfast:
            breakfast_penalty = -15  # Example fixed breakfast price per person
            breakfast_penalties = breakfast_penalty * sum(
                room.amounts for room in day_accommodation.room_details
            )
            day_total += breakfast_penalties
            day_details.append(f"No Breakfast minus 15$ each room: {breakfast_penalty} x Total rooms = {breakfast_penalties}")

        total_price += day_total
        day_details.append(f"Total for day {day_accommodation.index}: {day_total}")
        detailed_breakdown.append("\n".join(day_details))

    return total_price, "\n\n".join(detailed_breakdown)



# Example usage
if __name__ == "__main__":
    price_file = {
        "single": {
            "summer": {"normal_day": 35, "weekend": 45},
            "winter": {"normal_day": 45, "weekend": 55},
            "special": {"normal_day": 55, "weekend": 55},
            "spring": {"normal_day": 55, "weekend": 55},
        },
        "twin": {
            "summer": {"normal_day": 55, "weekend": 65},
            "winter": {"normal_day": 65, "weekend": 75},
            "special": {"normal_day": 75, "weekend": 85},
            "spring": {"normal_day": 75, "weekend": 85},
        },
        "apartment": {
            "summer": {"normal_day": 99, "weekend": 99},
            "winter": {"normal_day": 99, "weekend": 99},
            "special": {"normal_day": 199, "weekend": 199},
            "spring": {"normal_day": 159, "weekend": 159},
        },
    }

    # Define a sample trip
    trip = TripAccommodationDetail(
        day_accommodation=[
            DayAccommodationDetail(
                index=1,
                room_details=[
                    RoomDetail(
                        amounts=2,
                        room_type=RoomType.SINGLE,
                        discount_list=[Discount(discount_type=DiscountType.CHILD_6_TO_12, discount_reason=15)],
                    )
                ],
                breakfast=0,
            )
        ]
    )

    start_date = datetime(2025, 5, 15)
    total_price, breakdown = calculate_trip_accommodation_price_with_details(trip, start_date, price_file)
    print(f"Total trip accommodation price: ${total_price:.2f}")
    print("\nBreakdown:")
    print(breakdown)
