from app.database import engine, Base, SessionLocal
from app.models.models import User
from app.core.security import hash_password

def init():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查测试用户是否存在
        test_user = db.query(User).filter(User.username == "test").first()
        if not test_user:
            print("Creating test user...")
            user = User(
                username="test",
                password=hash_password("123456")
            )
            db.add(user)
            db.commit()
            print("Test user created successfully!")
        else:
            print("Test user already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    init()
