from src.controller import USER_CONTROLLER, CLASSROOM_CONTROLLER, POST_CONTROLLER, ASSIGNMENT_CONTROLLER
from fastapi import FastAPI


app = FastAPI()


app.include_router(USER_CONTROLLER)
app.include_router(CLASSROOM_CONTROLLER)
app.include_router(POST_CONTROLLER)
app.include_router(ASSIGNMENT_CONTROLLER)