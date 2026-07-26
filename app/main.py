import time
import logging
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
load_dotenv()
from fastapi import FastAPI, Request, HTTPException, status
from Ratelimiter import RateLimiter

app = FastAPI()

limiter = RateLimiter()


@app.get("/health")
async def root():
    logger.info("Checked health of application: Healthy")
    return {"message": "Application is healthy"}

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logger.info(f"IP-Adress - {request.headers.get('ip_address')}")
    start_time = time.perf_counter()
    obj = getattr(limiter, os.environ.get("algoritm", "TokenBucket"))
    response = obj(request.headers.get('ip_address'))
    if response == False:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests. Please try again later."}
        )
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    logger.info(f"Time took to respond - {str(process_time)}")
    response.headers["X-Process-Time"] = str(process_time)
    return response

