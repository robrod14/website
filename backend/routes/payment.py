# routes/payment.py
import qrcode
from flask import Blueprint, send_file, jsonify
from io import BytesIO
from database import SessionLocal
from models import Registration, Event

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/qr/<reg_id>", methods=["GET"])
def payment_qr(reg_id):
    """Generate a Venmo QR code for a given registration"""
    db = SessionLocal()
    reg = db.query(Registration).get(reg_id)
    if not reg:
        return jsonify({"error": "Registration not found"}), 404

    event = db.query(Event).get(reg.event_id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    if not reg.payment_memo:
        return jsonify({"error": "No payment memo set"}), 400

    amount = event.price_cents / 100.0
    memo = reg.payment_memo

    venmo_url = (
        f"venmo://paycharge?txn=pay&recipients=YourVenmoHandle"
        f"&amount={amount}&note={memo}"
    )

    # Generate QR code
    img = qrcode.make(venmo_url)
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(buf, mimetype="image/png")
