from schema import WineDetail
from prompt import Prompt, get_json_format_instructions

WINE_DETAIL_EXTRACTION_PROMPT = """
You are an experienced hote employee, and your task is to determine whether the customer requests winery services based on their requirements. If not, return false; if yes, return true along with the relevant information. You need to extract the following details:
1. The number of wine bottles the customer wants to taste, if not specify in user request, leave null, don't guess.
2. The number of hours the customer wants to rent the winery. if not specify in user request, leave null, don't guess.
3. Information about the meal the customer uses at the winery. There are two types of meals: Winery Meal 1, Winety Meal 2 and please include meal only in this 2 types. If not specify in user request, leave null, don't guess.
"""
wine_detail_extraction_prompt = Prompt(
    name="Wine Detail Extraction",
    instruction= WINE_DETAIL_EXTRACTION_PROMPT,
    output_format_instruction= get_json_format_instructions(WineDetail),
    examples=[],
    input_keys=["description"],
    output_key="output",
    output_type="json"
)
