from fastapi import FastAPI

from src.middlewares.log_middleware import log_request_data
from src.routes import user_router, queue_router

app = FastAPI(
    title="First API",
    description="Repo for engaging your knowledge",
    version="1.0.0",
)
app.middleware("http")(log_request_data)


app.include_router(user_router.router)
app.include_router(queue_router.router)


@app.get("/")
async def read_root():
    return {"Author": "SonND"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
