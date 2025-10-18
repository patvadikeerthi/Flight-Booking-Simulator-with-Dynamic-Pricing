# backend/pricing_engine.py
from datetime import datetime
import math

def calculate_dynamic_fare(base_price: float, total_seats: int, booked_seats: int, departure_ts: datetime, demand_level: str) -> float:
    """
    Combine seat availability, time-to-departure and demand to compute dynamic fare.
    Returns float rounded to 2 decimals.
    """
    if total_seats <= 0:
        return round(base_price, 2)

    remaining_pct = max(0.0, (total_seats - booked_seats) / total_seats)  # fraction 0..1
    days_to_departure = (departure_ts - datetime.utcnow()).days

    # Seat multiplier
    if remaining_pct > 0.5:
        seat_mult = 1.0
    elif remaining_pct > 0.2:
        seat_mult = 1.12
    else:
        seat_mult = 1.35

    # Time multiplier
    if days_to_departure > 30:
        time_mult = 1.0
    elif days_to_departure > 15:
        time_mult = 1.08
    elif days_to_departure > 7:
        time_mult = 1.18
    else:
        time_mult = 1.40

    # Demand multiplier
    demand_map = {"low": 1.0, "medium": 1.06, "high": 1.18}
    demand_mult = demand_map.get(demand_level, 1.0)

    price = base_price * seat_mult * time_mult * demand_mult

    # Round to nearest 0.5 or cents (choose cents)
    return round(price, 2)
