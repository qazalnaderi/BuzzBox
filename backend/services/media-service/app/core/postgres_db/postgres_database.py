import sqlalchemy
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:admin@new_postgres_container:5432/mailservice"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Base = sqlalchemy.orm.declarative_base()

AsyncSessionLocal = sessionmaker(
    bind=engine,  # Bind the engine to the sessionmaker
    class_=AsyncSession,  # Specify AsyncSession class for asynchronous operations
    expire_on_commit=False,  # Prevent automatic session expiration after commit
)

async def get_db():
    async with AsyncSessionLocal() as db:
        try:
            yield db  # Yield the session to the route handler
        except SQLAlchemyError as e:
            # Log or handle the error explicitly
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
        finally:
            # Ensure the session is properly closed after the operation
            await db.close()