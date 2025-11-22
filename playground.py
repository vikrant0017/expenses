import asyncio
from datetime import datetime
from decimal import Decimal

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.models import Base, User, Group, Expense, Split

# Database URL
# Assuming postgres user/password from compose.yaml and default port 5432
DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/postgres"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)

    # Create tables
    # Note: In production, use Alembic for migrations.
    # This is just for the playground to ensure tables exist.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all) # Clean slate for playground
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        async with session.begin():
            # 1. Create Users
            alice = User(name="Alice")
            bob = User(name="Bob")
            charlie = User(name="Charlie")
            session.add_all([alice, bob, charlie])
        
        # Flush to get IDs
        await session.commit() 

        async with session.begin():
            # 2. Create Group
            trip_group = Group(name="Road Trip")
            session.add(trip_group)
            
            # 3. Add Users to Group
            # We need to re-fetch or merge if we closed the transaction, 
            # but here we are in a new transaction with same session context if we didn't close session.
            # However, objects might be detached if expire_on_commit=True (default).
            # We set expire_on_commit=False, so they should be usable.
            
            trip_group.users.append(alice)
            trip_group.users.append(bob)
            trip_group.users.append(charlie)

        await session.commit()

        async with session.begin():
            # 4. Create Expense
            # Alice pays 120.00 for "Gas"
            expense = Expense(
                group_id=trip_group.id,
                user_id=alice.id,
                title="Gas",
                description="Fuel for the car",
                amount=Decimal("120.00"),
                timestamp=datetime.utcnow()
            )
            session.add(expense)
            await session.flush() # to get expense.id

            # 5. Create Splits
            # Split equally: 40 each
            split1 = Split(group_id=trip_group.id, expense_id=expense.id, user_id=alice.id, amount=Decimal("40.00"))
            split2 = Split(group_id=trip_group.id, expense_id=expense.id, user_id=bob.id, amount=Decimal("40.00"))
            split3 = Split(group_id=trip_group.id, expense_id=expense.id, user_id=charlie.id, amount=Decimal("40.00"))
            
            session.add_all([split1, split2, split3])

        await session.commit()

        # 6. Verify Data
        print("\n--- Verification ---")
        
        # Fetch Users
        result = await session.execute(select(User).order_by(User.id))
        users = result.scalars().all()
        print(f"Users: {users}")

        # Fetch Group and its Users
        result = await session.execute(select(Group).where(Group.name == "Road Trip"))
        group = result.scalar_one()
        # Accessing relationship requires eager loading or awaitable attribute access if lazy (default)
        # But we can just use select to fetch related if needed, or rely on lazy loading failing in async without explicit options.
        # Let's use explicit join or select for demonstration.
        # Actually, for simple verification, let's just print the group.
        print(f"Group: {group}")
        
        # To fetch users in group properly in async:
        # await session.refresh(group, ["users"]) 
        # print(f"Group Users: {group.users}")
        
        # Fetch Expenses
        result = await session.execute(select(Expense).where(Expense.group_id == group.id))
        expenses = result.scalars().all()
        for exp in expenses:
            print(f"Expense: {exp.title} paid by User ID {exp.user_id} Amount: {exp.amount}")
            
            # Fetch Splits for this expense
            result_splits = await session.execute(select(Split).where(Split.expense_id == exp.id))
            splits = result_splits.scalars().all()
            for s in splits:
                print(f"  - Split: User ID {s.user_id} owes {s.amount}")

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
