from src.controller import (
    USER_CONTROLLER,
    CLASSROOM_CONTROLLER,
    POST_CONTROLLER,
    ASSIGNMENT_CONTROLLER,
    AUTH_CONTROLLER,
    NOTIFICATION_CONTROLLER,
    ATTN_CONTROLLER
)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  #
)

app.include_router(USER_CONTROLLER)
app.include_router(CLASSROOM_CONTROLLER)
app.include_router(POST_CONTROLLER)
app.include_router(ASSIGNMENT_CONTROLLER)
app.include_router(AUTH_CONTROLLER)
app.include_router(NOTIFICATION_CONTROLLER)
app.include_router(ATTN_CONTROLLER)
