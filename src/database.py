from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# PostgreSQL connection information
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/consumer"

# Create engine
engine = create_engine(DATABASE_URL)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class to define models
Base = declarative_base(metadata=MetaData())


def check_db_connection():
    """Check the database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Successfully connected to the database!")
            return True
    except Exception as e:
        print("Failed to connect to the database. Error:", e)
        return False


# Dependency to get the session from the database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
