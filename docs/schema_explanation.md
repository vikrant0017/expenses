# Expenses App Schema Documentation

This document explains the database schema and SQLAlchemy models for the Expenses application.

## Overview

The application manages expenses shared among groups of users. The core entities are:

- **Users**: Individuals who participate in groups and expenses.
- **Groups**: Collections of users who share expenses (e.g., "Trip to Vegas", "Housemates").
- **Expenses**: A cost incurred by a user within a group.
- **Splits**: The breakdown of an expense, detailing how much each user in the group owes.

## Database Schema

The schema is implemented in PostgreSQL.

### Tables

#### 1. `users`
Represents a registered user.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Primary Key. Unique identifier. |
| `name` | `varchar` | The user's name. |

#### 2. `groups`
Represents a group of users.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Primary Key. Unique identifier. |
| `name` | `varchar` | The group's name. |

#### 3. `user_group`
A many-to-many association table linking users to groups.

| Column | Type | Description |
| :--- | :--- | :--- |
| `user_id` | `integer` | Foreign Key to `users.id`. |
| `group_id` | `integer` | Foreign Key to `groups.id`. |

#### 4. `expenses`
Represents a single expense event.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Primary Key. |
| `group_id` | `integer` | Foreign Key to `groups.id`. The group this expense belongs to. |
| `user_id` | `integer` | Foreign Key to `users.id`. The user who **paid** the expense. |
| `title` | `varchar` | Short title of the expense. |
| `description` | `varchar` | Optional detailed description. |
| `amount` | `numeric(10,2)` | Total amount paid. |
| `timestamp` | `timestamp` | When the expense occurred. |
| `created_at` | `timestamp` | Record creation time. |
| `updated_at` | `timestamp` | Record update time. |

#### 5. `splits`
Represents the share of an expense for a specific user.

| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | `integer` | Primary Key. |
| `group_id` | `integer` | Foreign Key to `groups.id`. |
| `expense_id` | `integer` | Foreign Key to `expenses.id`. |
| `user_id` | `integer` | Foreign Key to `users.id`. The user who **owes** this share. |
| `amount` | `numeric(10,2)` | The amount this user owes. |

## SQLAlchemy Models

The application uses SQLAlchemy ORM to map these tables to Python classes. The models are defined in `app/models.py`.

### Key Relationships

- **User <-> Group**: Many-to-Many via `UserGroup`.
    - `User.groups`: List of groups the user belongs to.
    - `Group.users`: List of users in the group.

- **Group -> Expense**: One-to-Many.
    - `Group.expenses`: List of all expenses in the group.
    - `Expense.group`: The group the expense belongs to.

- **User -> Expense**: One-to-Many.
    - `User.expenses`: List of expenses paid by the user.
    - `Expense.user`: The user who paid.

- **Expense -> Split**: One-to-Many.
    - `Expense.splits`: List of split records for the expense.
    - `Split.expense`: The parent expense.

### Example Usage

```python
# Creating a new expense with splits
expense = Expense(
    group_id=group.id,
    user_id=payer.id,
    title="Dinner",
    amount=Decimal("100.00"),
    timestamp=datetime.utcnow()
)

# Adding splits
split1 = Split(expense=expense, user_id=user1.id, amount=Decimal("50.00"), group_id=group.id)
split2 = Split(expense=expense, user_id=user2.id, amount=Decimal("50.00"), group_id=group.id)

session.add(expense)
session.add_all([split1, split2])
await session.commit()
```
