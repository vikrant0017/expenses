from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    groups: Mapped[List["Group"]] = relationship(
        secondary="user_group", back_populates="users"
    )
    expenses: Mapped[List["Expense"]] = relationship(back_populates="user")
    splits: Mapped[List["Split"]] = relationship(back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, name={self.name})>"


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    users: Mapped[List["User"]] = relationship(
        secondary="user_group", back_populates="groups"
    )
    expenses: Mapped[List["Expense"]] = relationship(back_populates="group")
    splits: Mapped[List["Split"]] = relationship(back_populates="group")

    def __repr__(self) -> str:
        return f"<Group(id={self.id}, name={self.name})>"


class UserGroup(Base):
    __tablename__ = "user_group"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), primary_key=True)


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    group: Mapped["Group"] = relationship(back_populates="expenses")
    user: Mapped["User"] = relationship(back_populates="expenses")
    splits: Mapped[List["Split"]] = relationship(
        back_populates="expense", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, title={self.title}, amount={self.amount})>"


class Split(Base):
    __tablename__ = "splits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    expense_id: Mapped[int] = mapped_column(ForeignKey("expenses.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    group: Mapped["Group"] = relationship(back_populates="splits")
    expense: Mapped["Expense"] = relationship(back_populates="splits")
    user: Mapped["User"] = relationship(back_populates="splits")

    def __repr__(self) -> str:
        return f"<Split(id={self.id}, amount={self.amount}, user_id={self.user_id})>"
