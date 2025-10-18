# backend/api.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from datetime import datetime
import io, json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from backend import crud
from backend.schemas import BookingRequest, BookingResponse

app = FastAPI(title="Flight Booking Simulator API")

# Search endpoint
@app.get("/search")
def search(origin: str = "", destination: str = ""):
    try:
        results = crud.search_flights(origin.strip().upper(), destination.strip().upper())
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Booking endpoint
@app.post("/book_multi", response_model=BookingResponse)
def book_multi(req: BookingRequest):
    try:
        payload = req.dict()
        result = crud.book_multi(payload)
        return {"pnr": result["pnr"], "total_price": result["total_price"], "status": "confirmed"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except RuntimeError as re:
        raise HTTPException(status_code=402, detail=str(re))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get booking & receipt
@app.get("/booking/{pnr}")
def get_booking(pnr: str):
    # Try to find booking details and receipt (depends on your schema)
    session = None
    try:
        from backend.db_config import get_session
        session = get_session()
        res = session.execute("SELECT * FROM Booking WHERE pnr_code = :pnr", {"pnr": pnr}).fetchone()
        if not res:
            raise HTTPException(status_code=404, detail="Booking not found")
        booking = dict(res)
        # try receipt
        try:
            rec = session.execute("SELECT payload_json FROM receipts WHERE booking_id = :bid ORDER BY receipt_id DESC LIMIT 1", {"bid": booking['booking_id']}).fetchone()
            receipt = json.loads(rec.payload_json) if rec else None
        except Exception:
            receipt = None
        return {"booking": booking, "receipt": receipt}
    finally:
        if session:
            session.close()

# Receipt PDF
@app.get("/receipt/{pnr}")
def receipt_pdf(pnr: str):
    # Get receipt payload
    session = None
    try:
        from backend.db_config import get_session
        session = get_session()
        row = session.execute("SELECT b.booking_id, r.payload_json FROM Booking b JOIN receipts r ON b.booking_id = r.booking_id WHERE b.pnr_code = :pnr ORDER BY r.receipt_id DESC LIMIT 1", {"pnr": pnr}).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Receipt not found")
        payload = json.loads(row.payload_json)

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        p.setFont("Helvetica", 12)
        p.drawString(40, 750, f"Flight Booking Receipt - PNR: {payload.get('pnr')}")
        p.drawString(40, 730, f"Flight ID: {payload.get('flight_id')}")
        p.drawString(40, 710, f"Seats: {payload.get('seats')}")
        p.drawString(40, 690, f"Total Price: ${payload.get('total_price')}")
        p.drawString(40, 670, f"Booking Time: {payload.get('booking_time')}")
        p.drawString(40, 650, "Passengers:")
        y = 630
        for psg in payload.get("passengers", []):
            line = f"- {psg.get('name')} | age:{psg.get('age')} | passport:{psg.get('passport')}"
            p.drawString(60, y, line)
            y -= 16
            if y < 80:
                p.showPage()
                y = 750
        p.showPage()
        p.save()
        buffer.seek(0)
        return FileResponse(buffer, media_type='application/pdf', filename=f"receipt_{pnr}.pdf")
    finally:
        if session:
            session.close()
