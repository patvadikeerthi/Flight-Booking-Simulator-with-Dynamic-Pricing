# backend/backend.py
from fastapi import FastAPI
from datetime import datetime
import random
from apscheduler.schedulers.background import BackgroundScheduler
from backend.pricing_engine import calculate_dynamic_fare
from backend.db_config import get_connection, init_db
from backend.models import FlightBooking

app = FastAPI(title="Flight Booking Simulator")

# Initialize DB
init_db()

# ----------------------------
# Background Simulation
# ----------------------------
def simulate_demand():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights")
    flights = cursor.fetchall()

    for flight in flights:
        seats_to_book = random.randint(0, 3)
        new_booked = min(flight["booked_seats"] + seats_to_book, flight["total_seats"])
        cursor.execute("UPDATE flights SET booked_seats=? WHERE flight_id=?", (new_booked, flight["flight_id"]))
        print(f"[{datetime.now()}] Flight {flight['flight_id']} booked seats: {new_booked}")

    conn.commit()
    conn.close()

scheduler = BackgroundScheduler()
scheduler.add_job(simulate_demand, 'interval', seconds=60)
scheduler.start()

# ----------------------------
# API: Search Flights
# ----------------------------
@app.get("/search")
def search_flights(origin: str, destination: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE origin=? AND destination=?", (origin, destination))
    flights = cursor.fetchall()
    results = []

    for flight in flights:
        demand_level = random.choice(["low", "medium", "high"])
        fare = calculate_dynamic_fare(
            flight["base_fare"],
            flight["total_seats"],
            flight["booked_seats"],
            datetime.fromisoformat(flight["departure"]),
            demand_level
        )
        results.append({
            "flight_id": flight["flight_id"],
            "origin": flight["origin"],
            "destination": flight["destination"],
            "departure": flight["departure"],
            "fare": fare,
            "available_seats": flight["total_seats"] - flight["booked_seats"]
        })

    conn.close()
    return results

# ----------------------------
# API: Book Flight
# ----------------------------
@app.post("/book")
def book_flight(booking: FlightBooking):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM flights WHERE flight_id=?", (booking.flight_id,))
    flight = cursor.fetchone()

    if not flight:
        conn.close()
        return {"error": "Flight not found"}

    available = flight["total_seats"] - flight["booked_seats"]
    if booking.seats > available:
        conn.close()
        return {"error": f"Only {available} seats available"}

    # Concurrency-safe update
    new_booked = flight["booked_seats"] + booking.seats
    cursor.execute("UPDATE flights SET booked_seats=? WHERE flight_id=?", (new_booked, booking.flight_id))

    # Generate PNR
    pnr = f"PNR{random.randint(1000,9999)}"
    cursor.execute(
        "INSERT INTO bookings (flight_id, seats_booked, pnr, booking_time) VALUES (?,?,?,?)",
        (booking.flight_id, booking.seats, pnr, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()

    return {
        "message": "Booking confirmed",
        "flight_id": booking.flight_id,
        "seats_booked": booking.seats,
        "pnr": pnr
    }
