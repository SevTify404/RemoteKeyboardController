import asyncio
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.security.all_instances import store_manager

from logging import getLogger

app_loger = getLogger("APP_LOG")

async def clean_up_task():
    """Permet de mettoyer les sessions expirés pour eviter de saturer la ram"""
    while True:
        try:
            
            store_manager.cleanup_expired_sessions()
            app_loger.info(f"Suppressions des sessions exirées")
        except Exception as e:
            app_loger.exception(f"Exception {e.__class__.__name__}: {e}")
            traceback.print_exc()
            
        await asyncio.sleep(3600)

# Lifespan : C'est lui qui va réguler le démarrage et l'extinction de l'app
@asynccontextmanager
async def lifespan(_ : FastAPI):

    #Code qui s'executera au démarrage de l'app FastApi
    asyncio.create_task(clean_up_task())

    # On expose l'appplication jusqu'à sa fin
    yield

    #Code qui s'executera au stop de l'app FastApi


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins = ['*'],
    allow_credentials=True,
    allow_methods = ['*'],
    allow_headers=["*"]
)

@app.get("/", include_in_schema=False)
async def root():
  return {"message": "Enjoyyyyyyy"}

# Utile exclusivement pour debugger en local, ne s'execute pas si on lance le serveur par uvicorn normalement
if __name__ == "__main__":
    conf = uvicorn.Config(app, port=8000, log_level='info')
    server = uvicorn.Server(conf)
    server.run()