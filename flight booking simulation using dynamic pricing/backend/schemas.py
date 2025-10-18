# backend/schemas.py
from pydantic import BaseModel
from typing import List, Optional

class FlightSearchResponse(BaseModel):
    flight_id: int
    flight_number: Optional[str] = None
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure: str
    base_price: float
    available_seats: int
    dynamic_fare: float

class Passenger(BaseModel):
    name: str
    age: Optional[int] = None
    passport: Optional[str] = None
    seat: Optional[str] = None

class BookingRequest(BaseModel):
    flight_id: int
    passengers: List[Passenger]
    simulate_payment: bool = True
    payment_success_rate: float = 0.95

class BookingResponse(BaseModel):
    pnr: str
    total_price: float
    status: str
