from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Thông tin kết nối PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/consumer"

# Tạo engine
engine = create_engine(DATABASE_URL)

# Tạo session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class để định nghĩa các model
Base = declarative_base(metadata=MetaData())


def check_db_connection():
    """Kiểm tra kết nối tới cơ sở dữ liệu."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Kết nối tới cơ sở dữ liệu thành công!")
            return True
    except Exception as e:
        print("Không thể kết nối tới cơ sở dữ liệu. Lỗi:", e)
        return False


# Dependency để lấy session từ database
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()