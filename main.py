from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from settings import PREFIX

import main_controller
import progress_controller
import coins_controller
import quests_controller
import rewards_controller


app = FastAPI(
    docs_url='/docs',
    openapi_url="/openapi.json",
    redoc_url=None,
    root_path=PREFIX
)


app.include_router(main_controller.router, tags=['common'])
app.include_router(progress_controller.router, tags=['progress'])
app.include_router(coins_controller.router, tags=['coins'])
app.include_router(quests_controller.router, tags=['quests'])
app.include_router(rewards_controller.router, tags=['rewards'])


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
