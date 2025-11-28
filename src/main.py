from fastapi import FastAPI
from api.v1.chat import router as chat_router

app = FastAPI(title="Messenger service")

app.include_router(chat_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
