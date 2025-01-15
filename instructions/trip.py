from schema import TripDetail
from prompt import Prompt, get_json_format_instructions

TRIP_DETAIL_EXTRACTION_PROMPT = "You are a hotel employee responsible for handling booking requests from customers. Your task is to analyze and extract detailed information about the services used by customers during their stay. Focus specifically on the services they use in different locations (e.g., cinema, podium) and provide a clear, day-by-day breakdown of their activities. For each customer request, follow these steps, Identify the time period (check-in and check-out dates) of the booking, Determine the number of people in the customer group. For each day of their stay, list the services they use (e.g., cinema, podium, spa, gym). Specify the type of buffets they eat and any beverages they consume. Do not include details about the rooms they book for overnight stays. Ensure the description follows a clear, day-by-day chronological order."
trip_detail_extraction_prompt = Prompt(
    name="Trip Detail Extraction",
    instruction= TRIP_DETAIL_EXTRACTION_PROMPT,
    output_format_instruction= get_json_format_instructions(TripDetail),
    examples=[],
    input_keys=["description"],
    output_key="output",
    output_type="json"
)
