# routes/admin.py
from flask import Blueprint, jsonify, request, session
from database import SessionLocal
from models import Registration, RegStatus, User, Event, AdminUser
from datetime import datetime
from routes.utils.sms import send_sms
from routes.utils.auth import require_admin_session
import os

admin_bp = Blueprint("admin", __name__)

# Credentials stored in env variables
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "changeme")

# ---------------------------
# Authentication Routes
# ---------------------------

@admin_bp.route("/login", methods=["POST"])
def admin_login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    db: Session = SessionLocal()
    admin = db.query(AdminUser).filter_by(username=username).first()
    db.close()

    print("Login attempt:", username, password)
    print("DB record:", admin.username if admin else None)
    print("Password match:", admin.check_password(password) if admin else None)


    if admin and admin.check_password(password):
        session["admin_logged_in"] = True
        session["admin_username"] = admin.username
        return jsonify({"message": "Login successful", "is_admin": True}), 200
    return jsonify({"error": "Invalid credentials"}), 401


@admin_bp.route("/logout", methods=["POST"])
@require_admin_session
def admin_logout():
    session.clear()
    resp = jsonify({"message": "Logged out"})
    resp.set_cookie("session", "", expires=0, httponly=True, samesite="Lax")
    return resp


# ---------------------------
# Existing Admin Routes
# ---------------------------

@admin_bp.route("/registrations/<reg_id>/confirm", methods=["POST"])
@require_admin_session
def confirm_paid(reg_id):
    """Mark a registration as paid (move from pending_payment to registered)
    and notify the organizer via SMS."""
    db = SessionLocal()
    reg = db.query(Registration).get(reg_id)
    if not reg:
        return jsonify({"error": "Registration not found"}), 404

    reg.status = RegStatus.registered
    reg.paid_at = datetime.utcnow()
    db.commit()

    # Notify Organizer
    event = db.query(Event).get(reg.event_id)
    if event and event.organizer_phone:
        msg = (
            f"✅ Payment confirmed!\n\n"
            f"Player: {reg.user.name}\n"
            f"Event: {reg.title}\n"
            f"Paid at: {reg.paid_at.strftime('%Y-%m-%d %H:%M:%S UTC')}"
        )
        try:
            send_sms(event.organizer_phone, msg)
        except Exception as e:
            return {"status": "registered", "sms_error": str(e)}, 500

    return {"status": "registered", "sms_sent": True}


@admin_bp.route("/events/<event_id>/registrations", methods=["GET"])
@require_admin_session
def list_event_registrations(event_id):
    """List all registrations for an event (admin view, includes phone numbers)"""
    db = SessionLocal()
    regs = db.query(Registration).filter(Registration.event_id == event_id).all()

    return jsonify([{
        "id": str(r.id),
        "user_name": r.user.name,
        "user_phone": r.user.phone_encrypted,  # admin sees phone
        "status": r.status.value,
        "payment_memo": r.payment_memo,
        "paid_at": r.paid_at.isoformat() if r.paid_at else None
    } for r in regs])


@admin_bp.route("/waitlist/<reg_id>/promote", methods=["POST"])
@require_admin_session
def promote_from_waitlist(reg_id):
    """
    Move a user from the waitlist to pending_payment 
    (e.g. when a registered player drops).
    """
    db = SessionLocal()
    reg = db.query(Registration).get(reg_id)
    if not reg:
        return jsonify({"error": "Registration not found"}), 404
    if reg.status != RegStatus.waitlist:
        return jsonify({"error": "Not on waitlist"}), 400

    reg.status = RegStatus.pending_payment
    db.commit()

    # Build QR link for this registration
    qr_url = f"https://yourdomain.com/api/payment/qr/{reg.id}"
    msg = (
        f"Hi {reg.user.name}, a spot just opened up!\n\n"
        f"To confirm, please pay using this Venmo QR: {qr_url}\n\n"
        f"Memo: {reg.payment_memo}"
    )

    try:
        send_sms(reg.user.phone_encrypted, msg)
    except Exception as e:
        return jsonify({"status": "pending_payment", "sms_error": str(e)}), 500

    return jsonify({
        "status": "pending_payment",
        "registration_id": str(reg.id),
        "sms_sent": True
    })


@admin_bp.route("/waitlist/<reg_id>/remove", methods=["DELETE"])
@require_admin_session
def remove_from_waitlist(reg_id):
    """Remove a user from the waitlist (if they can’t join)"""
    db = SessionLocal()
    reg = db.query(Registration).get(reg_id)
    if not reg:
        return jsonify({"error": "Registration not found"}), 404
    if reg.status != RegStatus.waitlist:
        return jsonify({"error": "Not on waitlist"}), 400

    db.delete(reg)
    db.commit()

    return jsonify({"removed": True, "registration_id": str(reg.id)})


@admin_bp.route("/events/<event_id>/organizer-phone", methods=["POST"])
@require_admin_session
def update_organizer_phone(event_id):
    """
    Update the organizer phone number for an event.
    Example payload:
    { "organizer_phone": "+15551234567" }
    """
    db = SessionLocal()
    data = request.json
    phone = data.get("organizer_phone")

    if not phone:
        return {"error": "organizer_phone is required"}, 400

    event = db.query(Event).get(event_id)
    if not event:
        return {"error": "event not found"}, 404

    event.organizer_phone = phone
    db.commit()

    return {
        "event_id": str(event.id),
        "organizer_phone": event.organizer_phone
    }


@admin_bp.route("/events/<event_id>/organizer-phone", methods=["GET"])
@require_admin_session
def get_organizer_phone(event_id):
    """
    Fetch the organizer phone number for a specific event.
    """
    db = SessionLocal()
    event = db.query(Event).get(event_id)
    if not event:
        return {"error": "event not found"}, 404

    return {
        "event_id": str(event.id),
        "title": event.title,
        "organizer_phone": event.organizer_phone
    }


@admin_bp.route("/events/organizers", methods=["GET"])
@require_admin_session
def list_event_organizers():
    """
    Fetch organizer phone numbers for all events (useful admin overview).
    """
    db = SessionLocal()
    events = db.query(Event).all()

    return jsonify([{
        "event_id": str(e.id),
        "title": e.title,
        "date": str(e.date),
        "organizer_phone": e.organizer_phone
    } for e in events])

# ✅ Admin status check
@admin_bp.route("/me", methods=["GET"])
def admin_me():
    """
    Return whether the current session is logged in as admin.
    Used by frontend Navbar to decide if logout should be shown.
    """
    #if session.get("admin_logged_in"):
    return jsonify({"is_admin": True, "username": session.get("admin_username")})
    #return jsonify({"is_admin": False}), 401

@admin_bp.route("/session", methods=["GET"])
def admin_session():
    if session.get("admin_logged_in"):
        return jsonify({
            "logged_in": True,
            "username": session.get("admin_username")
        })
    return jsonify({"logged_in": False})

