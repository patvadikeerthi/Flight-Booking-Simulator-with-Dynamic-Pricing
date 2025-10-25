// frontend/static/js/app.js
const API_BASE = (function(){
  return window.location.origin; // same host as served (FastAPI)
})();

window.searchFlights = async function() {
  const origin = document.getElementById('origin').value.trim().toUpperCase();
  const destination = document.getElementById('destination').value.trim().toUpperCase();
  const resultsEl = document.getElementById('results');
  resultsEl.innerHTML = '<div class="text-muted">Searching…</div>';
  try {
    const res = await fetch(`${API_BASE}/search?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}`);
    if (!res.ok) {
      resultsEl.innerHTML = `<div class="alert alert-warning">No flights found or backend error.</div>`;
      return;
    }
    const flights = await res.json();
    if (!flights || flights.length === 0) {
      resultsEl.innerHTML = `<div class="alert alert-info">No flights available.</div>`;
      return;
    }
    resultsEl.innerHTML = '';
    flights.forEach(f => {
      const card = document.createElement('div');
      card.className = 'flight-card';
      card.innerHTML = `
        <div class="d-flex justify-content-between">
          <div>
            <h5>Flight ${f.flight_id}: ${f.origin} → ${f.destination}</h5>
            <div class="small-muted">Departure: ${f.departure} · Available seats: ${f.available_seats} · Demand: ${f.demand}</div>
          </div>
          <div class="text-end">
            <h4 class="text-success">₹${f.fare}</h4>
            <button class="btn btn-outline-primary btn-sm" onclick="openBooking(${f.flight_id}, ${f.fare})">Book</button>
          </div>
        </div>
      `;
      resultsEl.appendChild(card);
    });
  } catch (err) {
    resultsEl.innerHTML = `<div class="alert alert-danger">Error contacting backend: ${err}</div>`;
  }
};

window.openBooking = function(flight_id, fare) {
  // navigate to booking page and prefill parameters
  const url = new URL(window.location.origin + '/booking-page');
  url.searchParams.set('flight_id', flight_id);
  url.searchParams.set('fare', fare);
  window.location.href = url.toString();
};

window.bookFlightFromForm = async function() {
  const flight_id = document.getElementById('flight_id').value;
  const passenger_name = document.getElementById('passenger_name').value;
  const email = document.getElementById('email').value;
  const fare = document.getElementById('fare').value;
  const resultEl = document.getElementById('bookResult');

  if (!flight_id || !passenger_name || !email || !fare) {
    resultEl.innerHTML = `<div class="alert alert-warning">Please fill all fields.</div>`;
    return;
  }

  try {
    const res = await fetch(`${API_BASE}/book`, {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({flight_id: Number(flight_id), passenger_name, email, fare: Number(fare)})
    });
    if (!res.ok) {
      const txt = await res.text();
      resultEl.innerHTML = `<div class="alert alert-danger">Booking failed: ${txt}</div>`;
      return;
    }
    const data = await res.json();
    resultEl.innerHTML = `<div class="alert alert-success">Booking confirmed! PNR: <strong>${data.pnr}</strong></div>`;
    // show download links
    const links = document.createElement('div');
    links.innerHTML = `
      <a class="btn btn-outline-primary btn-sm mt-2" href="${data.pdf}" target="_blank">Open PDF Receipt</a>
      <a class="btn btn-outline-secondary btn-sm mt-2" href="${data.json}" download>Download JSON</a>
    `;
    resultEl.appendChild(links);
  } catch (err) {
    resultEl.innerHTML = `<div class="alert alert-danger">Error placing booking: ${err}</div>`;
  }
};

window.bookFlight = async function(flight_id, fare) {
  // quick helper to call book API
  const passenger_name = prompt("Passenger name:");
  if (!passenger_name) return;
  const email = prompt("Email:");
  if (!email) return;
  try {
    const res = await fetch(`${API_BASE}/book`, {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({flight_id: Number(flight_id), passenger_name, email, fare: Number(fare)})
    });
    if (!res.ok) {
      alert("Booking failed: " + await res.text());
      return;
    }
    const d = await res.json();
    alert("Booking confirmed! PNR: " + d.pnr);
    // open booking page
    window.location.href = '/mybookings?pnr=' + d.pnr;
  } catch (err) {
    alert("Error: " + err);
  }
};

window.viewBooking = async function() {
  const pnr = document.getElementById('pnr').value.trim();
  if (!pnr) { alert('Enter PNR'); return; }
  const detail = document.getElementById('bookingDetail');
  detail.innerHTML = 'Loading...';
  try {
    const res = await fetch(`${API_BASE}/booking/${encodeURIComponent(pnr)}`);
    if (!res.ok) {
      detail.innerHTML = `<div class="alert alert-warning">Booking not found.</div>`;
      return;
    }
    const b = await res.json();
    detail.innerHTML = `
      <div class="card p-3">
        <h5>PNR: ${b.pnr}</h5>
        <div><strong>Passenger:</strong> ${b.passenger_name}</div>
        <div><strong>Email:</strong> ${b.email}</div>
        <div><strong>Flight ID:</strong> ${b.flight_id}</div>
        <div><strong>Fare:</strong> ₹${b.fare}</div>
        <div><strong>Status:</strong> ${b.status}</div>
        <div><strong>Booked at:</strong> ${b.booking_time}</div>
      </div>
    `;
  } catch (err) {
    detail.innerHTML = `<div class="alert alert-danger">Error: ${err}</div>`;
  }
};

window.cancelBooking = async function() {
  const pnr = document.getElementById('pnr').value.trim();
  if (!pnr) { alert('Enter PNR'); return; }
  if (!confirm('Cancel booking ' + pnr + '?')) return;
  try {
    const res = await fetch(`${API_BASE}/cancel/${encodeURIComponent(pnr)}`, {method: 'DELETE'});
    if (!res.ok) {
      alert('Cancellation failed: ' + await res.text());
      return;
    }
    const r = await res.json();
    alert(r.message);
    document.getElementById('bookingDetail').innerHTML = '';
  } catch (err) {
    alert('Error: ' + err);
  }
};

// Prefill booking page if query string present
(function prefillBookingFromQuery(){
  const params = new URLSearchParams(window.location.search);
  const fid = params.get('flight_id');
  const fare = params.get('fare');
  if (fid) document.getElementById('flight_id') && (document.getElementById('flight_id').value = fid);
  if (fare) document.getElementById('fare') && (document.getElementById('fare').value = fare);
})();
