from fastapi import FastAPI
from .api import router

app = FastAPI(title="StressTesterCLI")
app.include_router(router)