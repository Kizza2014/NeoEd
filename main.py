from fastapi import FastAPI
from controller import book_controller, user_controller, cart_controller, transaction_controller
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount('/static/thumbnail', StaticFiles(directory="static/thumbnail"), name="thumbnail")


app.include_router(book_controller)
app.include_router(user_controller)
app.include_router(cart_controller)
app.include_router(transaction_controller)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)