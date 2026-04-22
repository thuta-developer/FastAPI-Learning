# seed.py
from database import SessionLocal
import model, auth

def create_initial_admin():
    db = SessionLocal()
    # admin ရှိမရှိ အရင်စစ်မယ်
    admin = db.query(model.User).filter(model.User.username == "superadmin").first()
    
    if not admin:
        new_admin = model.User(
            username="admin",
            email="admin@gmail.com",
            hashed_password=auth.hash_password("superuser"), # password ကို ဒီမှာ ပေးပါ
            is_staff=True 
        )
        db.add(new_admin)
        db.commit()
        print("✅ Superadmin created successfully!")
    else:
        print("ℹ️ Admin already exists.")
    db.close()

if __name__ == "__main__":
    create_initial_admin()