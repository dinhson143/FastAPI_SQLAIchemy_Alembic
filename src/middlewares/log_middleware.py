import time
from fastapi import Request


async def log_request_data(request: Request, call_next):
    """
    Middleware to log request information and processing time.
    """
    # Before the request is processed
    start_time = time.time()
    print(f"Middleware: Request URL: {request.url}")
    print(f"Middleware: Request method: {request.method}")

    response = await call_next(request)  # Pass the request to the route handler

    # After the response is processed
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Middleware: Process time: {process_time:.2f} seconds")
    return response
