from fastapi import APIRouter
from app.api.v1 import produits
from app.api.v1 import jobs

v1_router = APIRouter()
v1_router.include_router(produits.router, prefix="/products", tags=["v1 Produits"])
v1_router.include_router(jobs.router, prefix='/jobs', tags=['v1 Jobs'])

from app.api.v1 import discord
v1_router.include_router(discord.router, prefix='/discord', tags=['v1 Discord'])
