from schema import TripAccommodationDetail
from prompt import Prompt, get_json_format_instructions

ACCOMODATION_DETAIL_EXTRACTION_PROMPT = """
You are a seasoned hotel professional, and your main responsibility each day is to handle guests’ requests. First, you determine how many nights they plan to stay. Then, using the hotel’s discount policies, you compile a list of the room types and the number of each type they wish to book, making sure to verify whether any discounts apply to those rooms. You must also confirm whether the guests will have breakfast. If they do not specify anything about breakfast, assume it is included.

The hotel’s current discount policies are as follows:

Rooms accommodating children under 6 years of age get a 50% discount.
Rooms accommodating children from 6 to 12 years of age get a 30% discount.
If the trip is organized through a travel company, every room type receives a 10% discount. In this case, a 10% discount automatically applies to all rooms.
If a room is booked for a relative of a hotel staff member, it qualifies for a 30% discount.
"""
accomodation_detail_extraction_prompt = Prompt(
    name="Accomodation Detail Extraction",
    instruction= ACCOMODATION_DETAIL_EXTRACTION_PROMPT,
    output_format_instruction= get_json_format_instructions(TripAccommodationDetail),
    examples=[],
    input_keys=["description"],
    output_key="output",
    output_type="json"
)
