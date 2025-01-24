from langgraph.graph import MessagesState, StateGraph, START, END
from instructions import *
from schema import *
from langchain_core.output_parsers import PydanticOutputParser
import typing as t
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import streamlit as st

# Initialize Streamlit app
st.title("🏨 Hotel Booking Assistant")
st.caption("Your personal concierge for hotel reservations and services")

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_KEY"))

# Load meal data
with open('data/buffet.json', 'r') as json_file:
    buffets = json.load(json_file)
with open('data/coffee_break.json', 'r') as json_file:
    coffee_breaks = json.load(json_file)

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Welcome to our Hotel Booking Service! Please describe your booking needs."}]

if "booking_state" not in st.session_state:
    st.session_state.booking_state = {
        "user_request": "",
        "trip_data": None,
        "accommodation_data": None,
        "winery_data": None,
        "meal_data": [],
        "place_data": [],
        "current_step": "trip",
        "meal_day": 1
    }

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Helper functions
def display_assistant_message(content):
    st.session_state.messages.append({"role": "assistant", "content": content})
    with st.chat_message("assistant"):
        st.markdown(content)

def is_trip_data_complete(trip_data: TripDetail) -> bool:
    required_fields = ["guest_amounts", "start_date", "number_of_day", "details"]
    return all(getattr(trip_data, field, None) for field in required_fields)

def process_trip_detail():
    try:
        extraction_prompt = trip_detail_extraction_prompt.to_string().format(description=st.session_state.booking_state["user_request"])
        parser = PydanticOutputParser(pydantic_object=TripDetail)
        response = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[{"role": "user", "content": extraction_prompt}],
            temperature=0.1,
        )
        trip = parser.parse(response.choices[0].message.content)
        
        if is_trip_data_complete(trip):
            st.session_state.booking_state.update({
                "trip_data": trip,
                "current_step": "accommodation"
            })
            return True
        else:
            missing_info = []
            if not trip.details: missing_info.append("trip details")
            if not trip.start_date: missing_info.append("start date")
            if not trip.guest_amounts: missing_info.append("guest amounts")
            if not trip.number_of_day: missing_info.append("number of days")
            
            polite_request = client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "system", "content": "You are a polite hotel assistant helping guests fill in missing trip details."},
                    {"role": "user", "content": f"Request: {', '.join(missing_info)}"}
                ],
                temperature=0.7,
            ).choices[0].message.content
            
            display_assistant_message(polite_request)
            return False
            
    except Exception as e:
        display_assistant_message(f"Sorry, I encountered an error: {str(e)}")
        return False
    
def is_accommodation_data_complete(accomodation_data: TripAccommodationDetail) -> bool:
    if len(accomodation_data.day_accommodation) == 0:
        return False
    elif len(accomodation_data.day_accommodation[0].room_details) == 0:
        return False
    else:
        return True

def process_accommodation_detail():
    print("Extract accommodation.....")
    try:
        while True:
            prompt = accomodation_detail_extraction_prompt.to_string().format(description=st.session_state.booking_state["user_request"])
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
                st.session_state.booking_state.update({
                    "accommodation_data": accommodation,
                    "current_step": "winery"
                })
                return True
            else:
                display_assistant_message("Can you specify the number of room you book for your trip in each day")
                return False   
    except Exception as e:
        display_assistant_message(f"Sorry, I encountered an error: {str(e)}")
        return False

def is_winery_data_complete(winery_data: WineDetail) -> bool:
    if not winery_data.is_winery:
        return True
    else:
        required_fields = ["bottle_amounts", "amount_of_times", "meals"]
        return all(getattr(winery_data.detail, field, None) for field in required_fields)

def process_winery_detail():
    print("Extract winery.....")
    try:
        prompt = wine_detail_extraction_prompt.to_string().format(description=st.session_state.booking_state["user_request"])
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
            st.session_state.booking_state.update({
                "winery_data": winery,
                "current_step": "places"
            })
            return True
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
            display_assistant_message(polite_request)
            return False
    except:
        display_assistant_message(f"Sorry, I encountered an error: {str(e)}")
        return False
    
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

def process_place_detail():
    print("Extract places.....")
    # while True:
    trip_place_detail = []
    for idx, day in enumerate(st.session_state.booking_state["trip_data"].details):
        description = day.description
        place_details: RentPlaces = extract_place_detail(description)
        trip_place_detail.append(place_details)
    st.session_state.booking_state.update({
        "place_data": trip_place_detail,
        "current_step": "meal"
    })
    return True
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

def process_meal_detail():
    day_index = st.session_state.booking_state["meal_day"]
    print(f"Extracting meals day {day_index}...")
    day =  st.session_state.booking_state["trip_data"].details[day_index-1]
    description = day.description
    meal_details: ListMealDetail = extract_meal_detail(description)
    complete, missing_data = is_meal_data_complete(meal_details)
    if complete:
        st.session_state.booking_state["meal_data"].append(meal_details)
        if day_index == len(st.session_state.booking_state["trip_data"].details):
            return True
        else:
            st.session_state.booking_state["meal_day"] += 1
            return False
    else:
        polite_request = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "system", "content": "You are a polite hotel assisstent helping guest fill in missing meals details. Rewrite the provided sentence."},
                {"role": "user", "content": f"We noticed some details are missing for the meals on day {day_index}. Could you kindly review the information below and provide the necessary details based on the menu?\n\n{missing_data}"}                    
            ],
            temperature=0.7,
        ).choices[0].message.content
        display_assistant_message(polite_request)
        st.session_state.booking_state["trip_data"].details[day_index - 1].description += f"Update missing data:\n {missing_data}"        
        return False

def process_step(step_name: str):
    step_processors = {
        "trip": process_trip_detail,
        "accommodation": process_accommodation_detail,
        "winery": process_winery_detail,
        "place": process_place_detail,
        "meal": process_meal_detail,
    }
    
    if step_name in step_processors:
        return step_processors[step_name]()
    else:
        raise ValueError(f"Invalid step name: {step_name}")

def display_booking_summary():
    booking = st.session_state.booking_state
    summary = [
        "## Booking Summary",
        f"**Guests:** {booking['trip_data'].guest_amounts}",
        f"**Dates:** {booking['trip_data'].start_date} ({booking['trip_data'].number_of_day} days)",
        f"**Rooms:** {len(booking['accommodation_data'].day_accommodation)} days booked",
        f"**Winery:** {'Yes' if booking['winery_data'].is_winery else 'No'}",
        f"**Places:** {len(booking['place_data'])} locations",
        f"**Meals:** {sum(len(day.buffets) for day in booking['meal_data'])} scheduled"
    ]
    display_assistant_message("\n".join(summary))

def process_user_input():
    current_step = st.session_state.booking_state["current_step"]
    next_step = {
        "trip": "accommodation",
        "accommodation": "winery",
        "winery": "place",
        "place": "meal",
        "meal": "complete"
    }
    if current_step in next_step:
        success = process_step(current_step)   
        if success:
            st.session_state.booking_state["current_step"] = next_step[current_step]
            return process_user_input()  # Recursive processing
    elif current_step == "complete":
        display_booking_summary()
                     
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    if st.session_state.booking_state["current_step"] != "meal":
        st.session_state.booking_state["user_request"] += prompt
    elif st.session_state.booking_state["current_step"] == "meal":
        day_index = st.session_state.booking_state["meal_day"]
        st.session_state.booking_state["trip_data"].details[day_index - 1].description += f"User Update: {prompt}"
    process_user_input()
    print(st.session_state.booking_state)

with st.sidebar:
    st.header("Booking Progress")
    steps = ["trip", "accommodation", "winery", "place", "meal", "complete"]
    current_idx = steps.index(st.session_state.booking_state["current_step"]) \
        if st.session_state.booking_state["current_step"] in steps else 0
    
    for i, step in enumerate(steps[:-1]):
        status = "✅" if i < current_idx else "➤" if i == current_idx else "◻️"
        st.write(f"{status} {step.capitalize()} Details")
    
    if st.button("Reset Booking"):
        st.session_state.clear()
        st.rerun()