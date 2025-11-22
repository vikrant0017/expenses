from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


# --- User Models ---
class UserBase(SQLModel):
    name: str

class User(UserBase, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    groups: List["Group"] = Relationship(back_populates="users", link_model="UserGroup")
    expenses: List["Expense"] = Relationship(back_populates="user")
    splits: List["Split"] = Relationship(back_populates="user")

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int


# --- Group Models ---
class GroupBase(SQLModel):
    name: str

class Group(GroupBase, table=True):
    __tablename__ = "groups"
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    users: List["User"] = Relationship(back_populates="groups", link_model="UserGroup")
    expenses: List["Expense"] = Relationship(back_populates="group")
    splits: List["Split"] = Relationship(back_populates="group")

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: int


# --- Link Models ---
class UserGroup(SQLModel, table=True):
    __tablename__ = "user_group"
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", primary_key=True)
    group_id: Optional[int] = Field(default=None, foreign_key="groups.id", primary_key=True)


# --- Expense Models ---
class ExpenseBase(SQLModel):
    title: str
    description: Optional[str] = None
    amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    group_id: int = Field(foreign_key="groups.id")
    user_id: int = Field(foreign_key="users.id") # Payer

class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) # Note: onupdate behavior needs manual handling or DB trigger in SQLModel usually, but for now keeping simple

    # Relationships
    group: Optional[Group] = Relationship(back_populates="expenses")
    user: Optional[User] = Relationship(back_populates="expenses")
    splits: List["Split"] = Relationship(back_populates="expense", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseRead(ExpenseBase):
    id: int
    timestamp: datetime
    created_at: datetime


# --- Split Models ---
class SplitBase(SQLModel):
    amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    group_id: int = Field(foreign_key="groups.id")
    expense_id: int = Field(foreign_key="expenses.id")
    user_id: int = Field(foreign_key="users.id")

class Split(SplitBase, table=True):
    __tablename__ = "splits"
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    group: Optional[Group] = Relationship(back_populates="splits")
    expense: Optional[Expense] = Relationship(back_populates="splits")
    user: Optional[User] = Relationship(back_populates="splits")
