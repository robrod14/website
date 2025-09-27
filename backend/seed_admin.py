#from app import db
#from models.admin_user import AdminUser

#def seed_admin():
#    username = "admin"
#    password = "M5%kYFoSus"  # choose a secure one!

#    if not AdminUser.query.filter_by(username=username).first():
#        admin = AdminUser(username=username)
#        admin.set_password(password)
#        db.session.add(admin)
#        db.session.commit()
#        print(f"Admin user '{username}' created with password '{password}'")
#    else:
#        print("Admin user already exists")

#if __name__ == "__main__":
#    seed_admin()

# seed_admin.py
from database import SessionLocal, engine
from models import AdminUser, Base
from sqlalchemy.sql.expression import select

Base.metadata.create_all(bind=engine)

def seed_admin():
    db = SessionLocal() # Create a session
    username = "admin"
    password = "hjkgjh32DgM5%kYFoSus452145jhgjk"

    # Use a direct SQLAlchemy query to find the user
    # Note: query is on the session, not the model class directly
    if not db.query(AdminUser).filter_by(username=username).first():
        admin = AdminUser(username=username)
        admin.set_password(password)
        db.add(admin) # Use db.add() instead of db.session.add()
        db.commit() # Use db.commit() instead of db.session.commit()
        print(f"Admin user '{username}' created with password '{password}'")
    else:
        print("Admin user already exists")

    print("DB URL:", engine.url)

    
    db.close() # Close the session after use

if __name__ == "__main__":
    seed_admin()