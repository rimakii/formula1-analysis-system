from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.auth.router import router as auth_router
from app.routers.drivers import router as drivers_router
from app.routers.constructors import router as constructors_router
from app.routers.circuits import router as circuits_router
from app.routers.races import router as races_router
from app.routers.results import router as results_router
from app.routers.analytics import router as analytics_router

app = FastAPI(
    title="F1 Analytics System",
    description="Информационная система для анализа и статистики гоночных команд Формулы 1",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(drivers_router)
app.include_router(constructors_router)
app.include_router(circuits_router)
app.include_router(races_router)
app.include_router(results_router)
app.include_router(analytics_router)

@app.get("/")
def root():
    return {
        "message": "F1 Analytics System API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
