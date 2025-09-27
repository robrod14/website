# inspect_db.py
from database import SessionLocal
from models import AdminUser

db = SessionLocal()
users = db.query(AdminUser).all()
for u in users:
    print("User in DB:", u.id, u.username, u.password_hash)
db.close()
