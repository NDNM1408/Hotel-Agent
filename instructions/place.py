from schema import RentPlaces
from prompt import Prompt, get_json_format_instructions

PLACE_DETAIL_EXTRACTION_PROMPT = """
As an experienced hotel employee, your responsibilities include extracting information from guest descriptions about the destinations they visit and the amenities they use at those locations. Additionally, based on the provided descriptions and any specified timeframes, you are tasked with determining whether the guest has rented the location for an entire day.
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