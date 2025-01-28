import sqlalchemy
from sqlalchemy.orm import sessionmaker
from fastapi import HTTPException


from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Set up your database URL for asynchronous operations
SQLALCHEMY_DATABASE_URL = "postgresql+asyncpg://postgres:admin@new_postgres_container:5432/mailservice"

# Create the async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
Base = sqlalchemy.orm.declarative_base()
# Create an async sessionmaker
AsyncSessionLocal = sessionmaker(
    bind=engine,  # Bind the engine to the sessionmaker
    class_=AsyncSession,  # Specify AsyncSession class for asynchronous operations
    expire_on_commit=False,  # Prevent automatic session expiration after commit
)

# Dependency for getting the DB session
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




# from databases import DatabaseURL
# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy_utils import database_exists, create_database
# from loguru import logger


# DATABASE_URL = "postgresql://postgres:admin@new_postgres_container:5432/mailservice"
# engine = create_engine(DATABASE_URL, future=True)
# session_local = sessionmaker(autoflush=False, autocommit=False, bind=engine)

# EntityBase = declarative_base()


# def init_db() -> bool:

#     EntityBase.metadata.create_all(bind=engine)
#     logger.info("Database Initialized")
#     return True

# logger.info(EntityBase.metadata.__tablename__)

# def get_db():
#     db = session_local()
#     try:
#         yield db
#     finally:
#         db.close()

