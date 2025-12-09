from datetime import UTC, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


def current_time():
    return datetime.now(UTC)


# ---- Link/Join Table ----
class UserGroup(SQLModel, table=True):
    __tablename__ = "user_group"  # pyright: ignore[reportAssignmentType]

    user_id: Optional[int] = Field(
        default=None, foreign_key="users.id", primary_key=True
    )
    group_id: Optional[int] = Field(
        default=None, foreign_key="groups.id", primary_key=True
    )


# --- User Models ---
class UserBase(SQLModel):
    pass


class User(UserBase, table=True):
    __tablename__ = "users"  # pyright: ignore[reportAssignmentType]
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(default=None, unique=True)
    name: str | None = None
    password: str  # hashed

    # Relationships
    groups: List["Group"] = Relationship(back_populates="users", link_model=UserGroup)
    expenses: List["Expense"] = Relationship(back_populates="user")
    splits: List["Split"] = Relationship(back_populates="user")


class UserCreate(UserBase):
    username: str
    password: str


class UserRead(UserBase):
    id: int
    name: str | None
    username: str


# --- Group Models ---
class GroupBase(SQLModel):
    name: str


class Group(GroupBase, table=True):
    __tablename__ = "groups"  # pyright: ignore[reportAssignmentType]
    id: Optional[int] = Field(default=None, primary_key=True)

    # Relationships
    users: List["User"] = Relationship(back_populates="groups", link_model=UserGroup)
    expenses: List["Expense"] = Relationship(back_populates="group")
    splits: List["Split"] = Relationship(back_populates="group")


class GroupCreate(GroupBase):
    pass


class GroupRead(GroupBase):
    id: int


# --- Link Models ---


# --- Expense Models ---
class ExpenseBase(SQLModel):
    title: str
    description: Optional[str] = None
    amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)

    # Note: Decimal gets dumped as string in json. I not sure if this the right choice thought
    # Should I instead let the frontend handle it.
    # @field_serializer("amount", when_used="json")
    # def convert_to_float(self, amount) -> float:
    #     return float(amount)


class Expense(ExpenseBase, table=True):
    __tablename__ = "expenses"  # pyright: ignore[reportAssignmentType]
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=current_time)
    created_at: datetime = Field(default_factory=current_time)
    updated_at: datetime = Field(
        default_factory=current_time
    )  # Note: onupdate behavior needs manual handling or DB trigger in SQLModel usually, but for now keeping simple
    group_id: int = Field(foreign_key="groups.id")
    user_id: int = Field(foreign_key="users.id")  # Payer

    # Relationships
    group: Optional[Group] = Relationship(back_populates="expenses")
    user: Optional[User] = Relationship(back_populates="expenses")
    splits: list["Split"] = Relationship(
        back_populates="expense",
        cascade_delete=True,
    )  # Cascade handled by ALchemy ORM


class ExpenseCreate(ExpenseBase):
    splits: list[
        "SplitCreate"
    ] = []  # Empty list as default since Expense splits relationship expects it to be a list
    group_id: int


class ExpenseRead(ExpenseBase):
    id: int
    timestamp: datetime
    created_at: datetime
    updated_at: datetime
    user_id: int
    group_id: int
    splits: Optional[list["Split"]] = None


# --- Split Models ---
class SplitBase(SQLModel):
    amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)


class Split(SplitBase, table=True):
    __tablename__ = "splits"  # pyright: ignore[reportAssignmentType]
    id: Optional[int] = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="groups.id")
    expense_id: int = Field(
        foreign_key="expenses.id", ondelete="CASCADE"
    )  # Cascade handled by DB
    user_id: int = Field(foreign_key="users.id")

    # Relationships
    group: Optional[Group] = Relationship(back_populates="splits")
    expense: Optional[Expense] = Relationship(back_populates="splits")
    user: Optional[User] = Relationship(back_populates="splits")


class SplitCreate(SplitBase):
    user_id: int


# --- Member Models (Sub Resource for relationship between user and group in UserGroup) ---
class Member(BaseModel):
    pass


class MemberCreateRequest(Member):
    id: int


class MemberCreate(Member):
    id: int
    group_id: int


class MemberReadRequest(Member):
    id: int | None = None
    group_id: int


class MemberRead(Member):
    id: int | None = None
    group_id: int
