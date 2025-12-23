import asyncio
import traceback
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import app_logger, log_startup_info, log_shutdown_info
from app.core.config import LOCAL_IP
from app.routes.auth_route import router as auth_router
from app.routes.ws_router import router as ws_router
from app.utils.security.all_instances import store_manager


async def clean_up_task():
    """Tâche de fond pour nettoyer les sessions expirées et éviter une saturation RAM"""
    while True:
        try:
            store_manager.cleanup_expired_sessions()
            app_logger.debug("Nettoyage des sessions expirées effectué avec succès")
        except Exception as e:
            app_logger.exception(f"Erreur lors du nettoyage des sessions: {e.__class__.__name__}")
            traceback.print_exc()
            
        await asyncio.sleep(3600)

# Lifespan : C'est lui qui va réguler le démarrage et l'extinction de l'app
@asynccontextmanager
async def lifespan(_ : FastAPI):
    # Code qui s'exécutera au démarrage de l'app FastAPI
    log_startup_info()
    print(f"📍 Serveur accessible sur:")
    print(f"   http://{LOCAL_IP}:8000")
    print(f"   http://localhost:8000")
    print(f"📚 Documentation: http://{LOCAL_IP}:8000/docs")

    # Créer la tâche de nettoyage
    asyncio.create_task(clean_up_task())

    # On expose l'appplication jusqu'à sa fin
    yield

    # Code qui s'exécutera à l'arrêt de l'app FastAPI
    log_shutdown_info("Arrêt du serveur")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"]
)

app.include_router(ws_router)
app.include_router(auth_router)

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Enjoyyyyyyy"}

# Utile exclusivement pour déboguer en local, ne s'exécute pas si on lance le serveur via uvicorn normalement
if __name__ == "__main__":
    conf = uvicorn.Config(app, port=8000, log_level='info', host='0.0.0.0')
    server = uvicorn.Server(conf)
    server.run()
