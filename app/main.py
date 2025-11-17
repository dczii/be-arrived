from fastapi import FastAPI
from app.routes import index
app = FastAPI()

@app.get("/")
def root():
    return {"message": "hello world"}

app.include_router(
    index.router,
    prefix= "/api"
)
