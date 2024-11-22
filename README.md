## Setup

* python -m venv venv
* venv\Scripts\activate
* pip install fastapi uvicorn pydantic[dotenv] alembic

## Các lệnh quan trọng trong Alembic

1. [x] alembic current Hiển thị version hiện tại của cơ sở dữ liệu.
2. [x] alembic history Liệt kê tất cả các migration đã tạo.
3. [x] alembic heads Hiển thị các version chưa được áp dụng.
4. [x] alembic show <version>	Hiển thị nội dung của migration cụ thể.
5. [x] alembic upgrade <version>	Nâng cấp cơ sở dữ liệu lên version cụ thể.
6. [x] alembic downgrade <version>	Quay lại version cụ thể.
7. [x] alembic stamp <version>	Gắn trạng thái cơ sở dữ liệu với version mà không chạy migration.
8. [x] alembic revision --autogenerate -m "your message"


## SQLAlchemy
1. [ ] SQLAlchemy Core
2. [ ] SQLAlchemy ORM
3. [ ] Thành phần chính trong SQLAlchemy: 
   * Engine
   * Metadata
   * Table
   * ORM (Object Relational Mapping)
   * Session