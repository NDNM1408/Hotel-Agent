from schema import RentPlaces
from prompt import Prompt, get_json_format_instructions

PLACE_DETAIL_EXTRACTION_PROMPT = """
As an experienced hotel employee, your primary responsibility is to extract key information from guest descriptions about their travel destinations and the specific amenities they utilize at those locations. Your tasks include the following:
1. Identify and record the destinations mentioned in the guest's descriptions, please extract the name of the place.
2. Amenity Extraction with Synonyms: Focus on identifying only the following amenities and their synonyms from the descriptions:
- Cinema: Includes synonyms like "theater",  "theater seating"
- School: Includes synonyms like "academy," "college," or "learning center."
- Dinner: Includes synonyms like "restaurant" or "dining."
- Boardroom: Includes synonyms like "conference room," "meeting room," or "business space."
- U-Table: Includes synonyms like "U-shaped table setup" or "U-style table arrangement."
- Party: Includes synonyms like "celebration," "event," or "gathering."
3. Based on the descriptions and any specified timeframes, determine whether the guest has rented the location for the entire day.
"""
place_detail_extraction_prompt = Prompt(
    name="Place Detail Extraction",
    instruction= PLACE_DETAIL_EXTRACTION_PROMPT,
    output_format_instruction= get_json_format_instructions(RentPlaces),
    examples=[],
    input_keys=["description"],
    output_key="output",
    output_type="json"
)