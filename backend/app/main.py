import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Lifespan : C'est lui qui va réguler le démarrage et l'extinction de l'app
@asynccontextmanager
async def lifespan(_ : FastAPI):

    #Code qui s'executera au démarrage de l'app FastApi

    # On expose l'appplication jusqu'à sa fin
    yield

    #Code qui s'executera au stop de l'app FastApi


app = FastAPI(lifespan=lifespan)

# Liste des origines autorisées
origins = [
    "http://localhost:5173" ## url front en local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
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