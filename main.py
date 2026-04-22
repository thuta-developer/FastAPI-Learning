from fastapi import FastAPI
from database import SessionLocal, engine
import model
from routers import items, users,admin

model.Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(items.router)
app.include_router(users.router)
app.include_router(admin.router)
@app.get("/")
async def root():
    return {"message": "API is working...."}
    