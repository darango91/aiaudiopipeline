from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi

from app.api.endpoints import audio, keywords, websockets
from app.core.config import settings

app = FastAPI(
    title="AI Audio Assistant API",
    description="Real-time audio processing with keyword detection",
    version="0.1.0",
    docs_url=None,  # Disable automatic docs to customize
    openapi_url=None  # Disable automatic OpenAPI schema to customize
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(audio.router, prefix="/audio", tags=["audio"])
app.include_router(keywords.router, prefix="/keywords", tags=["keywords"])
app.include_router(websockets.router, prefix="/ws", tags=["websockets"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/test")
def test_endpoint():
    return {"message": "Backend test endpoint is working!"}
    

@app.get("/api/test")
def api_test_endpoint():
    return {"message": "Backend API test endpoint is working!"}


@app.get("/openapi.json", include_in_schema=False)
async def get_open_api_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )


@app.get("/api/docs", include_in_schema=False)
async def get_documentation():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - Swagger UI"
    )


@app.get("/docs", include_in_schema=False)
async def get_documentation_redirect():
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{app.title} - Swagger UI"
    )


@app.get("/api/openapi.json", include_in_schema=False)
async def get_api_openapi_endpoint():
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
