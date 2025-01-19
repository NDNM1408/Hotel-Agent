from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

import typing as t
from langgraph.graph import MessagesState
from langgraph import StateGraph, START, END
from schema import *

class InputStates(t.TypedDict):
    user_text: str

class OutputStates(t.TypedDict):
    final_summary: str

class BookingState(MessagesState):
    user_text: str
    trip_data: TripDetail
    accom_data: TripAccommodationDetail
    meal_data: t.List[ListMealDetail]
    
class Agent:
    def __init__(self, buffets, coffee_breaks):
        self.client = OpenAI(api_key=os.getenv("OPENAI_KEY"))
        self.model_name = os.getenv("MODEL_NAME")
        self.buffets = buffets
        self.coffee_breaks = coffee_breaks
    
    