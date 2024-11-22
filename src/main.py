from fastapi import FastAPI

from src.routes import user_router

app = FastAPI(
    title="BookStore API",
    description="API for managing users",
    version="1.0.0",
)

app.include_router(user_router.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
