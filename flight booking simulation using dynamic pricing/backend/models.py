# backend/models.py
from pydantic import BaseModel
from datetime import datetime

class FlightSearch(BaseModel):
    origin: str
    destination: str

class FlightBooking(BaseModel):
    flight_id: int
    seats: int = 1
