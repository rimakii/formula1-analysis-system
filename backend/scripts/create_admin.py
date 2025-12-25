import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth.security import get_password_hash

def create_admin():
    db: Session = SessionLocal()

    print("=== Создание администратора F1 Analytics System ===")
    email = input("Введите email администратора: ")
    password = input("Введите пароль: ")
    full_name = input("Введите полное имя (опционально): ")

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"Ошибка: Пользователь с email {email} уже существует!")
        return

    admin_user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name if full_name else None,
        is_active=True,
        is_admin=True
    )

    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    print(f"\n✓ Администратор успешно создан!")
    print(f"  Email: {admin_user.email}")
    print(f"  ID: {admin_user.user_id}")
    print(f"  Admin: {admin_user.is_admin}")

    db.close()

if __name__ == "__main__":
    create_admin()
