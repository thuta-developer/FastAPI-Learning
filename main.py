from fastapi import FastAPI
from database import SessionLocal, engine
import model
from routers import items, users

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(items.router)
app.include_router(users.router)
@app.get("/")
async def root():
    return {"message": "Hello World"}
    