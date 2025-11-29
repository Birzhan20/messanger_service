from fastapi import FastAPI
from api.v1 import chat

app = FastAPI(title="Messanger service")

app.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
