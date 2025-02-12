from langgraph.graph import MessagesState, StateGraph, START, END
from instructions import *
from schema import *
from langchain_core.output_parsers import PydanticOutputParser
import typing as t
from openai import OpenAI
import os
from dotenv import load_dotenv
import json

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_KEY"))  # Replace with your actual API key
with open('data/buffet.json', 'r') as json_file:
    buffets = json.load(json_file)
with open('data/coffee_break.json', 'r') as json_file:
    coffee_breaks = json.load(json_file)

class InputStates(t.TypedDict):
    user_request: str

class OutputStates(t.TypedDict):
    
    final_summary: str

class BookingState(MessagesState):
    trip_data: t.Optional[TripDetail] = None
    accommodation_data: t.Optional[TripAccommodationDetail] = None
    winery_data: t.Optional[WineDetail] = None
    meal_data: t.List[ListMealDetail] = []
    place_data: t.List[RentPlaces] = []

def is_trip_data_complete(trip_data: TripDetail) -> bool:
    required_fields = ["guest_amounts", "start_date", "number_of_day", "details"]
    return all(getattr(trip_data, field, None) for field in required_fields)

def extract_trip_detail(state: InputStates) -> BookingState:
    print("Extract trip.....")
    while True:
        prompt = trip_detail_extraction_prompt.to_string().format(description=state['user_request'])
        parser = PydanticOutputParser(pydantic_object=TripDetail)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        generated_text = response.choices[0].message.content
        trip = parser.parse(generated_text)

        if is_trip_data_complete(trip):
            return {"trip_data": trip, "accommodation_data": None, "meal_data": []}
        else:
            missing_info = []
            if not trip.details:
                missing_info.append("trip details")
            if not trip.start_date:
                missing_info.append("start date")
            if not trip.guest_amounts:
                missing_info.append("guest amounts")
            if not trip.number_of_day:
                missing_info.append("number of days")
            polite_request = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a polite hotel assisstent helping guest fill in missing trip details."},
                    {"role": "user", "content": f"The following information is missing: {', '.join(missing_info)}. Please ask the user politely to provide it."}
                ],
                temperature=0.7,
            ).choices[0].message.content
            # Request user to provide the missing details
            print(polite_request)
            user_update = input(f"Your response: ")
            state['user_request'] += f" {user_update}"  # Append user-provided information to the request
            
def is_accommodation_data_complete(accomodation_data: TripAccommodationDetail) -> bool:
    if len(accomodation_data.day_accommodation) == 0:
        return False
    elif len(accomodation_data.day_accommodation[0].room_details) == 0:
        return False
    else:
        return True

def extract_accommodation_detail(state: InputStates) -> BookingState:
    print("Extract accommodation.....")
    while True:
        prompt = accomodation_detail_extraction_prompt.to_string().format(description=state['user_request'])
        parser = PydanticOutputParser(pydantic_object=TripAccommodationDetail)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )

        generated_text = response.choices[0].message.content
        accommodation = parser.parse(generated_text)
        if is_accommodation_data_complete(accommodation):
            return {"accommodation_data": accommodation}
        else:
            print("Can you specify the number of room you book for your trip in each day")
            user_update = input(f"Your response: ")
            state['user_request'] += f" {user_update}"   
             
def extract_place_detail(description: str):
    prompt = place_detail_extraction_prompt.to_string().format(description=description)
    parser = PydanticOutputParser(pydantic_object=RentPlaces)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
    )
    generated_text = response.choices[0].message.content
    places = parser.parse(generated_text)
    return places

def extract_places(state: BookingState) -> BookingState:
    print("Extract places.....")
    # while True:
    trip_place_detail = []
    for idx, day in enumerate(state["trip_data"].details):
        description = day.description
        place_details: RentPlaces = extract_place_detail(description)
        trip_place_detail.append(place_details)
    return {"place_data": trip_place_detail}


def is_winery_data_complete(winery_data: WineDetail) -> bool:
    if not winery_data.is_winery:
        return True
    else:
        required_fields = ["bottle_amounts", "amount_of_times", "meals"]
        return all(getattr(winery_data.detail, field, None) for field in required_fields)

def extract_winery_detail(state: InputStates) -> BookingState:
    print("Extract winery.....")
    while True:
        prompt = wine_detail_extraction_prompt.to_string().format(description=state['user_request'])
        parser = PydanticOutputParser(pydantic_object=WineDetail)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        generated_text = response.choices[0].message.content
        winery = parser.parse(generated_text)
        if is_winery_data_complete(winery):
            return {'winery_data': winery}
        else:
            missing_info = []
            if not winery.detail.bottle_amounts:
                missing_info.append("Amounts of winery bottle guests want to try")
            if not winery.detail.amount_of_times:
                missing_info.append("Amount of time guests want to rent the winery")
            if not winery.detail.meals:
                missing_info.append("Meal guests want to use at the winery")

            polite_request = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a polite hotel assisstent helping guest fill in missing winery details."},
                    {"role": "user", "content": f"The following information is missing: {', '.join(missing_info)}. Please ask the user politely to provide it."}                    
                ],
                temperature=0.7,
            ).choices[0].message.content
            print(polite_request)
            user_update = input(f"Your response: ")
            state['user_request'] += f"Winery Update: {user_update}"  # Append user-provided information to the request


def is_meal_data_complete(meals: ListMealDetail):
    missing_data = ""
    complete = True

    for index, meal in enumerate(meals.buffets):  # Use enumerate for correct indexing
        if meal.meal_type == MealType.COFFEE_BREAK:
            if not meal.meal_name or meal.meal_name.lower() not in coffee_breaks:
                complete = False
                time = meal.meal_time.strftime("%H:%M:%S") if meal.meal_time else "No Information"
                missing_data += f"{index + 1}, Time: {time}, Coffee Break\n"
        elif meal.meal_type == MealType.NORMAL:
            if not meal.meal_name or meal.meal_name.lower() not in buffets:
                complete = False
                time = meal.meal_time.strftime("%H:%M:%S") if meal.meal_time else "No Information"
                missing_data += f"{index + 1}, Time: {time}, Buffets\n"

    return complete, missing_data


def extract_meal_detail(description: str):
    prompt = meal_detail_extraction_prompt.to_string().format(description=description)
    parser = PydanticOutputParser(pydantic_object=ListMealDetail)
    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
    )

    generated_text = response.choices[0].message.content
    meals = parser.parse(generated_text)
    return meals


def extract_meals(state: BookingState) -> BookingState:
    print("Extracting meals...")
    trip_meal_detail = []

    for idx, day in enumerate(state["trip_data"].details):
        while True:
            description = day.description
            meal_details: ListMealDetail = extract_meal_detail(description)
            complete, missing_data = is_meal_data_complete(meal_details)

            if complete:
                trip_meal_detail.append(meal_details)
                break  # Exit the loop when meals are complete
            else:
                print(f"Missing data for meals on day {idx + 1}. Can you provide the missing information based on the menu?\n{missing_data}")
                user_update = input("Your response: ")
                day.description += f"\nUser update: {user_update}"  # Append user update for re-extraction

    return {"meal_data": trip_meal_detail}
            
        

graph = StateGraph(BookingState, input=InputStates)
graph.add_node("trip_node", extract_trip_detail)
graph.add_node("accommodation_node", extract_accommodation_detail)
graph.add_node("place_node", extract_places)
graph.add_node("winery_node", extract_winery_detail)
graph.add_node("meal_node", extract_meals)

graph.add_edge(START, "trip_node")
graph.add_edge("trip_node", "accommodation_node")
graph.add_edge("accommodation_node", "place_node")
graph.add_edge("place_node", "winery_node")
graph.add_edge("winery_node", "meal_node")
graph.add_edge("meal_node", END)

graph = graph.compile()

sample_description = """
· Dates: April 10–11, 2025 (Thursday and Friday).

· Event Type: Partner Day for Dell Technologies.

· Number of Guests: ~50 VIP attendees.

· Requirements:

o Rooms: 20 rooms with twin beds; the remaining guests will not stay overnight. There will be 10 room have children less than 6 years old

o Program:

§ 1:30 PM – Welcome coffee break.

§ 2:00 PM – 5:00 PM – Presentations in the Knight's Hall (theater seating, podium, technical equipment).

§ Evening Program: Free time or wellness, followed by a wine tasting, buffet, and socializing at the Winery.

§ Next Day: Breakfast, 10:00 AM – 12:00 PM presentations, coffee break, 12:30 PM buffet lunch at Restaurant Pálffy.
"""


print(graph.invoke({"user_request": sample_description}))
