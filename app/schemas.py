from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# --- User Schemas ---
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Group Schemas ---
class GroupBase(BaseModel):
    name: str

class GroupCreate(GroupBase):
    pass

class GroupRead(GroupBase):
    id: int
    
    model_config = ConfigDict(from_attributes=True)

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    title: str
    description: Optional[str] = None
    amount: Decimal

class ExpenseCreate(ExpenseBase):
    group_id: int
    user_id: int # Payer

class ExpenseRead(ExpenseBase):
    id: int
    group_id: int
    user_id: int
    timestamp: datetime
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
