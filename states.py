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
    final_summary: t.Optional[str]