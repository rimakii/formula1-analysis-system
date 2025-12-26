from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.routers import drivers, races, constructors, circuits, analytics, results, batch

app = FastAPI(title="F1 Analytics System", version="1.0.0")

app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

app.include_router(drivers.router, prefix="/api", tags=["Drivers"])
app.include_router(races.router, prefix="/api", tags=["Races"])
app.include_router(constructors.router, prefix="/api", tags=["Constructors"])
app.include_router(circuits.router, prefix="/api", tags=["Circuits"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(results.router, prefix="/api", tags=["Results"])
app.include_router(batch.router, prefix="/api", tags=["Batch Operations"])
