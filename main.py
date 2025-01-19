from openai import OpenAI
import os
from dotenv import load_dotenv
from nodes import extract_trip_detail, extract_meal_detail, extract_accommodation_detail
from schema import *
load_dotenv()


client = OpenAI(api_key=os.getenv("OPENAI_KEY"))  # Replace with your actual API key
sample_description = """
· Dates: April 10–11, 2025 (Thursday and Friday).

· Event Type: Partner Day for Dell Technologies.

· Number of Guests: ~50 VIP attendees.

· Requirements:

o Rooms: 20 rooms with twin beds; the remaining guests will not stay overnight. There will be 10 room have children less than 6 years old
This trip is 

o Program:

§ 1:30 PM – Welcome coffee break.

§ 2:00 PM – 5:00 PM – Presentations in the Knight's Hall (theater seating, podium, technical equipment).

§ Evening Program: Free time or wellness, followed by a wine tasting, buffet, and socializing at the Winery.

§ Next Day: Breakfast, 10:00 AM – 12:00 PM presentations, coffee break, 12:30 PM buffet lunch at Restaurant Pálffy.
"""


trip: TripDetail = extract_trip_detail(sample_description, client)
print("======================TRIP=================\n")
print(trip.model_dump())

accommodation: TripAccommodationDetail = extract_accommodation_detail(sample_description, client)
print("======================ACCOMMODATION=================\n")
print(accommodation.model_dump())

for idx, day in enumerate(trip.details):
    print(f"======================DAY {idx}=================\n")
    description = day.description
    meal_details: ListMealDetail = extract_meal_detail(description, client)
    print(meal_details.model_dump())


