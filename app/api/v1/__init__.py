from fastapi import APIRouter
from app.api.v1 import (
    produits, jobs, cron
)

v1_router = APIRouter()
v1_router.include_router(produits.router, prefix="/products", tags=["v1 Produits"])
v1_router.include_router(jobs.router, prefix='/jobs', tags=['v1 Jobs'])
v1_router.include_router(cron.router, prefix='/cron', tags=['v1 Cron'])

from app.api.v1 import discord
v1_router.include_router(discord.router, prefix='/discord', tags=['v1 Discord'])
