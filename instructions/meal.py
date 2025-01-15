from schema import ListMealDetail
from prompt import Prompt, get_json_format_instructions


MEAL_DETAIL_EXTRACTION_PROMPT = "As a seasoned hotel professional, your role is to carefully review the guest’s requests. Based on their description, you will itemize the meals they wish to reserve throughout the day and include any additional details they specify for each meal."
meal_detail_extraction_prompt = Prompt(
    name="Meal Detail Extraction",
    instruction= MEAL_DETAIL_EXTRACTION_PROMPT,
    output_format_instruction= get_json_format_instructions(ListMealDetail),
    examples=[],
    input_keys=["description"],
    output_key="output",
    output_type="json"
)
