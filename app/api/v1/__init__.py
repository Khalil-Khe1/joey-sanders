from fastapi import APIRouter
from app.api.v1 import (
    jobs, cron, tiqets
)

v1_router = APIRouter()
v1_router.include_router(jobs.router, prefix='/jobs', tags=['v1 Jobs'])
v1_router.include_router(cron.router, prefix='/cron', tags=['v1 Cron'])
v1_router.include_router(tiqets.router, prefix='/tiqets', tags=['v1 Tiqets'])

#from app.api.v1 import discord
#v1_router.include_router(discord.router, prefix='/discord', tags=['v1 Discord'])
