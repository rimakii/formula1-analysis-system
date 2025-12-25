from fastapi import FastAPI
from app.auth.router import router as auth_router
from app.routers import drivers, races, constructors, circuits

app = FastAPI(title="F1 Analytics System", version="1.0.0")

# ???????? auth ??????
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])

# ?????? ???????
app.include_router(drivers.router, prefix="/api", tags=["Drivers"])
app.include_router(races.router, prefix="/api", tags=["Races"])
# ? ?.?.
