from openai import OpenAI
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from schema import *
from instructions.trip import trip_detail_extraction_prompt
# from instructions.acommodation import 
from instructions.meal import meal_detail_extraction_prompt

load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_KEY"))  # Replace with your actual API key
sample_description = """
· Dates: April 10–11, 2025 (Thursday and Friday).

· Event Type: Partner Day for Dell Technologies.

· Number of Guests: ~50 VIP attendees.

· Requirements:

o Rooms: 20 rooms with twin beds; the remaining guests will not stay overnight.

o Program:

§ 1:30 PM – Welcome coffee break.

§ 2:00 PM – 5:00 PM – Presentations in the Knight's Hall (theater seating, podium, technical equipment).

§ Evening Program: Free time or wellness, followed by a wine tasting, buffet, and socializing at the Winery.

§ Next Day: Breakfast, 10:00 AM – 12:00 PM presentations, coffee break, 12:30 PM buffet lunch at Restaurant Pálffy.
"""

sample1 = """
"1:30 PM – Welcome coffee break. 2:00 PM – 5:00 PM – Presentations in the Knight's Hall (theater seating, podium, technical equipment). Evening Program: Free time or wellness, followed by a wine tasting, buffet, and socializing at the Winery.
"""

sample2 = """
Breakfast in the morning. 10:00 AM – 12:00 PM presentations. Coffee break. 12:30 PM buffet lunch at Restaurant Pálffy.
"""
# ============================== TEST TRIP =======================
# test = trip_detail_extraction_prompt.to_string().format(description=sample_description)
# parser = PydanticOutputParser(pydantic_object=TripDetail)
# response = client.chat.completions.create(
#     model='gpt-4o-mini',
#     messages=[
#         {"role": "user", "content": test}
#     ],
#     temperature=0.1,
# )

# Extract and return the generated text
# generated_text = response.choices[0].message.content
# trip = parser.parse(generated_text)
# print(trip.model_dump())

# ============================== TEST ACCOMMODATION =======================
# test = trip_detail_extraction_prompt.to_string().format(description=sample_description)
# parser = PydanticOutputParser(pydantic_object=TripDetail)
# response = client.chat.completions.create(
#     model='gpt-4o-mini',
#     messages=[
#         {"role": "user", "content": test}
#     ],
#     temperature=0.1,
# )

# Extract and return the generated text
# generated_text = response.choices[0].message.content
# trip = parser.parse(generated_text)
# print(trip.model_dump())

# ============================== TEST BUFFET =======================
test1 = meal_detail_extraction_prompt.to_string().format(description=sample1)
test2 = meal_detail_extraction_prompt.to_string().format(description=sample2)

parser = PydanticOutputParser(pydantic_object=ListMealDetail)
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "user", "content": test1}
    ],
    temperature=0.1,
)

generated_text = response.choices[0].message.content
trip = parser.parse(generated_text)
print("================================")
print(trip.model_dump())

response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[
        {"role": "user", "content": test2}
    ],
    temperature=0.1,
)

generated_text = response.choices[0].message.content
trip = parser.parse(generated_text)
print(trip.model_dump())

