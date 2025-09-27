# routes/events.py
from flask import Blueprint, request, jsonify
from database import SessionLocal
from models import Event, User, Registration, RegStatus
from routes.utils.auth import require_admin_session

events_bp = Blueprint("events", __name__)

@events_bp.route("/", methods=["GET"])
def list_events():
    """Return all events with basic info (for public site)"""
    db = SessionLocal()
    events = db.query(Event).all()
    return jsonify([{
        "id": e.id,
        "title": e.title,
        "location": e.location,
        "date": e.date.isoformat() if e.date else None,
        "time": e.time,
        "capacity": e.capacity,
        "price_cents": e.price_cents,
        "is_signups_open": e.is_signups_open
    } for e in events])

@events_bp.route("/<event_id>/register", methods=["POST"])
def register(event_id):
    """Register a user for an event. Either as pending_payment or waitlist."""
    db = SessionLocal()
    data = request.json or {}
    name, phone = data.get("name"), data.get("phone")

    if not name or not phone:
        return jsonify({"error": "Name and phone required"}), 400

    event = db.query(Event).get(event_id)
    if not event or not event.is_signups_open:
        return jsonify({"error": "Event not open"}), 400

    # count current registered (already paid)
    paid_count = db.query(Registration).filter(
        Registration.event_id == event.id,
        Registration.status == RegStatus.registered
    ).count()

    # create user (later: encrypt phone properly)
    user = User(name=name, phone_encrypted=phone)
    db.add(user)
    db.commit()
    db.refresh(user)

    # decide if goes straight to waitlist
    status = RegStatus.pending_payment if paid_count < event.capacity else RegStatus.waitlist

    reg = Registration(event_id=event.id, user_id=user.id, status=status)
    db.add(reg)
    db.commit()
    db.refresh(reg)

    # attach a unique memo for Venmo
    reg.payment_memo = f"PB-{event.id}-{reg.id}"
    db.commit()

    return jsonify({
        "registration_id": str(reg.id),
        "status": status.value,
        "payment_memo": reg.payment_memo,
        "payment_instructions": f"Scan QR at /api/payment/qr/{reg.id}"
    }), 201

# --------------------- ADMIN ONLY ROUTES ------------------------- #

@events_bp.route("/", methods=["POST"])
@require_admin_session
def create_event():
    """
    Admin-only: create a new event
    """
    db = SessionLocal()
    data = request.json

    required_fields = ["title", "location", "date", "time", "capacity", "price_cents", "organizer_phone"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    event = Event(
        title=data["title"],
        location=data["location"],
        date=data["date"],
        time=data["time"],
        capacity=int(data["capacity"]),
        price_cents=int(data["price_cents"]),
        is_signups_open=data.get("is_signups_open", True),
        organizer_phone=data["organizer_phone"]
    )

    db.add(event)
    db.commit()
    db.refresh(event)

    return jsonify({
        "id": str(event.id),
        "title": event.title,
        "location": event.location,
        "date": str(event.date),
        "time": str(event.time),
        "capacity": event.capacity,
        "price_cents": event.price_cents,
        "organizer_phone": event.organizer_phone,
        "is_signups_open": event.is_signups_open
    }), 201

@events_bp.route("/<event_id>", methods=["PUT"])
@require_admin_session
def update_event(event_id):
    """Admin: update event details"""
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    if not event:
        return {"error": "event not found"}, 404

    data = request.json
    for field in ["title", "location", "date", "time", "capacity", "price_cents", "is_signups_open", "organizer_phone"]:
        if field in data:
            setattr(event, field, data[field])

    db.commit()
    db.refresh(event)

    return jsonify({
        "id": str(event.id),
        "title": event.title,
        "location": event.location,
        "date": str(event.date),
        "time": str(event.time),
        "capacity": event.capacity,
        "price_cents": event.price_cents,
        "organizer_phone": event.organizer_phone,
        "is_signups_open": event.is_signups_open
    })


@events_bp.route("/<event_id>", methods=["DELETE"])
@require_admin_session
def delete_event(event_id):
    """Admin: delete an event"""
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    if not event:
        return {"error": "event not found"}, 404

    db.delete(event)
    db.commit()
    return {"status": "deleted", "event_id": str(event_id)}


@events_bp.route("/<event_id>/toggle-signups", methods=["POST"])
@require_admin_session
def toggle_signups(event_id):
    """Admin: open/close signups"""
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    if not event:
        return {"error": "event not found"}, 404

    event.is_signups_open = not event.is_signups_open
    db.commit()
    return {
        "event_id": str(event.id),
        "is_signups_open": event.is_signups_open
    }