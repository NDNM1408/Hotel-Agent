import os
import json
import typing as t
from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langgraph.graph import MessagesState, StateGraph, START, END
from openai import OpenAI
from instructions import *
from schema import *

load_dotenv()

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


class Agent:
    def __init__(self, api_key: str, buffet_file: str, coffee_break_file: str):
        self.client = OpenAI(api_key=api_key)
        with open(buffet_file, 'r') as json_file:
            self.buffets = json.load(json_file)
        with open(coffee_break_file, 'r') as json_file:
            self.coffee_breaks = json.load(json_file)
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(BookingState, input=InputStates)
        graph.add_node("trip_node", self.extract_trip_detail)
        graph.add_node("accommodation_node", self.extract_accommodation_detail)
        graph.add_node("place_node", self.extract_places)
        graph.add_node("winery_node", self.extract_winery_detail)
        graph.add_node("meal_node", self.extract_meals)

        graph.add_edge(START, "trip_node")
        graph.add_edge("trip_node", "accommodation_node")
        graph.add_edge("accommodation_node", "place_node")
        graph.add_edge("place_node", "winery_node")
        graph.add_edge("winery_node", END)

        return graph.compile()

    def is_trip_data_complete(self, trip_data: TripDetail) -> bool:
        required_fields = ["guest_amounts", "start_date", "number_of_day", "details"]
        return all(getattr(trip_data, field, None) for field in required_fields)

    def extract_trip_detail(self, state: InputStates) -> BookingState:
        print("Extracting trip details...")
        while True:
            prompt = trip_detail_extraction_prompt.to_string().format(description=state['user_request'])
            parser = PydanticOutputParser(pydantic_object=TripDetail)
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )
            generated_text = response.choices[0].message.content
            trip = parser.parse(generated_text)

            if self.is_trip_data_complete(trip):
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
                polite_request = self.client.chat.completions.create(
                    model='gpt-4o-mini',
                    messages=[
                        {"role": "system", "content": "You are a polite hotel assistant helping guests fill in missing trip details."},
                        {"role": "user", "content": f"The following information is missing: {', '.join(missing_info)}. Please ask the user politely to provide it."}
                    ],
                    temperature=0.7,
                ).choices[0].message.content
                print(polite_request)
                user_update = input("Your response: ")
                state['user_request'] += f" {user_update}"

    def is_accommodation_data_complete(self, accommodation_data: TripAccommodationDetail) -> bool:
        if len(accommodation_data.day_accommodation) == 0:
            return False
        elif len(accommodation_data.day_accommodation[0].room_details) == 0:
            return False
        else:
            return True

    def extract_accommodation_detail(self, state: InputStates) -> BookingState:
        print("Extracting accommodation details...")
        while True:
            prompt = accomodation_detail_extraction_prompt.to_string().format(description=state['user_request'])
            parser = PydanticOutputParser(pydantic_object=TripAccommodationDetail)
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
            )

            generated_text = response.choices[0].message.content
            accommodation = parser.parse(generated_text)
            if self.is_accommodation_data_complete(accommodation):
                return {"accommodation_data": accommodation}
            else:
                print("Can you specify the number of rooms you book for your trip each day?")
                user_update = input("Your response: ")
                state['user_request'] += f" {user_update}"
    
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
                        {"role": "system", "content": "You are a polite hotel assisstent helping guest fill in missing trip details at winery service."},
                        {"role": "user", "content": f"The following information is missing: {', '.join(missing_info)}. Please ask the user politely to provide it."}
                    ],
                    temperature=0.7,
                ).choices[0].message.content
                print(polite_request)
                user_update = input(f"Your response: ")
                state['user_request'] += f"Winery Update: {user_update}"  # Append user-provided information to the request

    def extract_places(self, state: BookingState) -> BookingState:
        print("Extracting places...")
        trip_place_detail = []
        for idx, day in enumerate(state["trip_data"].details):
            description = day.description
            place_details: RentPlaces = self.extract_place_detail(description)
            trip_place_detail.append(place_details)
        return {"place_data": trip_place_detail}

    def extract_place_detail(self, description: str):
        prompt = place_detail_extraction_prompt.to_string().format(description=description)
        parser = PydanticOutputParser(pydantic_object=RentPlaces)
        response = self.client.chat.completions.create(
            model='gpt-4o-mini',
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
        )
        generated_text = response.choices[0].message.content
        return parser.parse(generated_text)

    def invoke(self, input_description: str):
        return self.graph.invoke({"user_request": input_description})

# Example Usage
if __name__ == "__main__":
    agent = Agent(api_key=os.getenv("OPENAI_KEY"), buffet_file='data/buffet.json', coffee_break_file='data/coffee_break.json')

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

    result = agent.invoke(sample_description)
    print(result)
