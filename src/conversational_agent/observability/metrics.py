from time import perf_counter

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.response import PlainTextResponse

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method","path","status_code"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP Request latency in seconds",
    ["method","path"],
    buckets=(0.01,0.05,0.1,0.5,1,2,5),
)

def register_metrics(app:FastAPI) -> None:
    @app.middleware("http")
    async def metrics_middleware(request: Request, call_next) -> Response:
        method = request.method
        path = request.url.path
        start = perf_counter()
        response = await call_next(request)
        duration = perf_counter() - start

        REQUEST_COUNT.labels(metho=method, path=path, status_code=str(response.status_code)).inc()
        REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
        return response
    
    @app.get("/metrics", tags=["observability"])
    def metrics() -> PlainTextResponse:
        return PlainTextResponse(generate_latest().decode("utf-8"),media_type=CONTENT_TYPE_LATEST)
