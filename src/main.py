from fastapi import FastAPI
from api.v1.chat import router as chat_router
from api.v1.support import router as support_router
import core.logger
import logging


app = FastAPI(title="Messenger service")

app.include_router(chat_router)
app.include_router(support_router)

logger = logging.getLogger(__name__)
logger.info("FastAPI app initialized")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
