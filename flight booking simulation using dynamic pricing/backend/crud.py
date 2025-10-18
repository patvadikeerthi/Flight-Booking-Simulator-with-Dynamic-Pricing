# backend/crud.py
import random, json
from datetime import datetime
from sqlalchemy import text
from backend.db_config import get_session
from backend.pricing_engine import calculate_dynamic_fare

def gen_pnr():
    t = datetime.utcnow().strftime("%y%m%d%H%M%S")
    rnd = random.randint(1000, 9999)
    return f"PNR{t}{rnd}"

def search_flights(origin: str, destination: str):
    """
    Return list of flights with dynamic fares (simulate demand randomly).
    """
    session = get_session()
    try:
        q = "SELECT flight_id, flight_number, departure_time, base_price, current_occupancy, aircraft_id, route_id FROM Flight WHERE 1=1"
        params = {}
        if origin:
            q += " AND route_id IN (SELECT route_id FROM Route WHERE origin_airport_code = :origin)"
            params['origin'] = origin
        if destination:
            q += " AND route_id IN (SELECT route_id FROM Route WHERE destination_airport_code = :destination)"
            params['destination'] = destination

        rows = session.execute(text(q), params).fetchall()
        results = []
        for r in rows:
            # fetch seats count & booked seats via queries (Seat and Booking tables)
            # We'll compute total seats as aircraft.total_capacity, current occupancy as Flight.current_occupancy
            # Fallbacks used if values missing
            # Get aircraft capacity
            cap_row = session.execute(text("SELECT total_capacity FROM Aircraft WHERE aircraft_id = :aid"), {"aid": r.aircraft_id}).fetchone()
            total_seats = cap_row.total_capacity if cap_row else 150
            booked = int(r.current_occupancy or 0)
            # parse departure_time
            departure = r.departure_time.isoformat() if hasattr(r.departure_time, "isoformat") else str(r.departure_time)
            demand = random.choice(["low", "medium", "high"])
            fare = calculate_dynamic_fare(float(r.base_price), total_seats, booked, r.departure_time, demand)
            results.append({
                "flight_id": r.flight_id,
                "flight_number": r.flight_number,
                "departure": departure,
                "base_price": float(r.base_price),
                "available_seats": max(0, total_seats - booked),
                "dynamic_fare": fare
            })
        return results
    finally:
        session.close()

def book_multi(booking_req):
    """
    booking_req: dict with flight_id,int passengers:list(dict), simulate_payment,bool, payment_success_rate
    Uses a database transaction and SELECT FOR UPDATE on Flight row to avoid race conditions.
    """
    session = get_session()
    try:
        # Open transaction
        with session.begin():
            # Lock the flight row
            row = session.execute(text("SELECT flight_id, base_price, current_occupancy, route_id, aircraft_id FROM Flight WHERE flight_id = :fid FOR UPDATE"), {"fid": booking_req['flight_id']}).fetchone()
            if not row:
                raise ValueError("Flight not found")

            # compute seating
            cap_row = session.execute(text("SELECT total_capacity FROM Aircraft WHERE aircraft_id = :aid"), {"aid": row.aircraft_id}).fetchone()
            total_seats = cap_row.total_capacity if cap_row else 150
            booked = int(row.current_occupancy or 0)

            seats_req = len(booking_req['passengers'])
            if seats_req > (total_seats - booked):
                raise ValueError(f"Only {total_seats - booked} seats available")

            # compute fare (use same demand for all seats)
            demand = booking_req.get("demand_level", random.choice(["low","medium","high"]))
            fare_per_seat = calculate_dynamic_fare(float(row.base_price), total_seats, booked, row.departure_time if hasattr(row, 'departure_time') else datetime.utcnow(), demand)
            total_price = round(fare_per_seat * seats_req, 2)

            # simulate payment
            if booking_req.get("simulate_payment", True):
                import random as _random
                if _random.random() >= booking_req.get("payment_success_rate", 0.95):
                    raise RuntimeError("Payment failed (simulated)")

            # update occupancy and insert booking & passengers & receipt
            new_occupancy = booked + seats_req
            session.execute(text("UPDATE Flight SET current_occupancy = :occ WHERE flight_id = :fid"), {"occ": new_occupancy, "fid": booking_req['flight_id']})

            pnr = gen_pnr()
            now = datetime.utcnow().isoformat()
            # Insert booking
            session.execute(text(
                "INSERT INTO Booking (pnr_code, flight_id, seat_id, total_fare_paid, passenger_name, booking_time) VALUES (:pnr, :fid, NULL, :price, :pname, :bt)"
            ), {"pnr": pnr, "fid": booking_req['flight_id'], "price": total_price, "pname": booking_req['passengers'][0]['name'] if booking_req['passengers'] else "N/A", "bt": now})

            # Get booking_id (Postgres returns via currval if serial) - fetch latest row
            booking_row = session.execute(text("SELECT booking_id FROM Booking WHERE pnr_code = :pnr"), {"pnr": pnr}).fetchone()
            booking_id = booking_row.booking_id

            # Insert passenger rows into passengers table (we reuse passenger table name 'passengers' if exists; adapt to your SQL)
            # The provided schema uses a separate passengers table in earlier snippets — if not present, skip.
            # We'll insert into 'passengers' table if it exists
            try:
                session.execute(text("SELECT 1 FROM passengers LIMIT 1"))
                has_passengers_table = True
            except Exception:
                has_passengers_table = False

            if has_passengers_table:
                for p in booking_req['passengers']:
                    session.execute(text("INSERT INTO passengers (booking_id, name, age, passport, seat) VALUES (:bid, :name, :age, :passport, :seat)"),
                                    {"bid": booking_id, "name": p.get('name'), "age": p.get('age'), "passport": p.get('passport'), "seat": p.get('seat')})

            # Insert into receipts if table exists
            try:
                session.execute(text("SELECT 1 FROM receipts LIMIT 1"))
                has_receipts_table = True
            except Exception:
                has_receipts_table = False

            if has_receipts_table:
                payload = {
                    "pnr": pnr,
                    "flight_id": booking_req['flight_id'],
                    "seats": seats_req,
                    "passengers": booking_req['passengers'],
                    "total_price": total_price,
                    "booking_time": now
                }
                session.execute(text("INSERT INTO receipts (booking_id, payload_json, created_at) VALUES (:bid, :payload, :ca)"),
                                {"bid": booking_id, "payload": json.dumps(payload), "ca": now})

            return {"pnr": pnr, "total_price": total_price}
    finally:
        session.close()
