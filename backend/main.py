import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from api.core.exception_handlers import api_exception_handlers
from api.core.limiter import limiter
from api.routers import router as api_router
from api.core.settings import settings


app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(api_router, prefix='/api')


@app.get('/health/')
async def health():
    return {'status': 'ok'}


api_exception_handlers(app)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=settings.cors.allow_credentials,
    allow_origins=settings.cors.allow_origins,
    allow_methods=settings.cors.allow_methods,
    allow_headers=settings.cors.allow_headers,
)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app.host,
        port=settings.app.port,
        reload=settings.app.reload
    )
