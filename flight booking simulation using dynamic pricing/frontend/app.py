# frontend/app.py
import streamlit as st
import requests, json
from datetime import datetime

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Flight Booking Simulator", layout="wide")
st.title("✈️ Flight Booking Simulator — Multi-step Booking")

# Step 1: Search
st.header("1 — Search Flights")
col1, col2 = st.columns(2)
with col1:
    origin = st.text_input("Origin (airport code)", "DEL")
with col2:
    destination = st.text_input("Destination (airport code)", "BOM")

if st.button("Search"):
    resp = requests.get(f"{API_BASE}/search", params={"origin": origin.strip().upper(), "destination": destination.strip().upper()})
    if resp.status_code != 200:
        st.error("Failed to fetch flights: " + resp.text)
    else:
        flights = resp.json()
        st.session_state['flights'] = flights
        st.success(f"Found {len(flights)} flights")

if 'flights' in st.session_state:
    st.subheader("Results")
    for f in st.session_state['flights']:
        st.markdown(f"**Flight {f['flight_id']}** — Fare: ${f['dynamic_fare']} — Available seats: {f['available_seats']}")
        if st.button(f"Select flight {f['flight_id']}", key=f"select_{f['flight_id']}"):
            st.session_state['selected_flight'] = f
            st.experimental_rerun()

# Step 2: Passenger details & book
if 'selected_flight' in st.session_state:
    st.header("2 — Passenger Info & Payment")
    flight = st.session_state['selected_flight']
    st.write(f"Selected flight {flight['flight_id']} — Fare per seat: ${flight['dynamic_fare']} — Available: {flight['available_seats']}")
    num = st.number_input("Passengers", min_value=1, max_value=flight['available_seats'], value=1)
    passengers = []
    for i in range(int(num)):
        st.subheader(f"Passenger {i+1}")
        name = st.text_input(f"Name {i+1}", key=f"name_{i}")
        age = st.number_input(f"Age {i+1}", min_value=0, max_value=120, key=f"age_{i}")
        passport = st.text_input(f"Passport {i+1}", key=f"passport_{i}")
        passengers.append({"name": name, "age": age, "passport": passport})

    simulate_payment = st.checkbox("Simulate payment", value=True)
    payment_rate = st.slider("Payment success rate", 0.0, 1.0, 0.95)

    if st.button("Confirm & Book"):
        payload = {
            "flight_id": flight['flight_id'],
            "passengers": passengers,
            "simulate_payment": simulate_payment,
            "payment_success_rate": payment_rate
        }
        res = requests.post(f"{API_BASE}/book_multi", json=payload)
        if res.status_code == 200:
            data = res.json()
            st.success(f"Booking confirmed! PNR: {data['pnr']} — Total: ${data['total_price']}")
            # fetch receipt
            try:
                r = requests.get(f"{API_BASE}/booking/{data['pnr']}")
                if r.status_code == 200:
                    book = r.json()
                    st.json(book.get('receipt'))
                    st.download_button("Download receipt (JSON)", data=json.dumps(book.get('receipt'), indent=2), file_name=f"receipt_{data['pnr']}.json", mime="application/json")
                    st.markdown(f"[Download PDF receipt]({API_BASE}/receipt/{data['pnr']})")
            except Exception as e:
                st.warning("Receipt fetch failed: " + str(e))
        else:
            try:
                err = res.json()
                st.error(f"Booking failed: {err.get('detail', err)}")
            except Exception:
                st.error("Booking failed.")

# Step 3: Manage booking
st.header("3 — Booking Management")
pnr_q = st.text_input("PNR to lookup/cancel")
if st.button("Get Booking"):
    if pnr_q:
        r = requests.get(f"{API_BASE}/booking/{pnr_q}")
        if r.status_code == 200:
            st.json(r.json())
            st.session_state['viewed_pnr'] = pnr_q
        else:
            st.error("Not found or error: " + r.text)

if st.button("Cancel Booking"):
    if 'viewed_pnr' in st.session_state:
        r = requests.post(f"{API_BASE}/cancel/{st.session_state['viewed_pnr']}")
        if r.status_code == 200:
            st.success("Cancelled")
        else:
            st.error("Cancel failed: " + r.text)
    else:
        st.warning("First lookup a booking")
