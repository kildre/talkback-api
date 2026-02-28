from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.admin.router import router as admin_router
from app.applicants.router import router as applicants_router
from app.auth.router import router as auth_router
from app.cases.router import router as cases_router
from app.chat.router import router as chat_router
from app.db import Base, engine
from app.health.router import router as health_router
from app.tts.router import router as tts_router
from app.users.router import router as users_router

# Create the app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database
Base.metadata.create_all(bind=engine)
# Add routes
app.include_router(cases_router)
app.include_router(applicants_router)

app.include_router(users_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(health_router)
app.include_router(chat_router)
app.include_router(tts_router)
