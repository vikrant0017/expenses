from sqlmodel import Session

from app.models import User, UserCreate


def create_user(session: Session, user: UserCreate):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
