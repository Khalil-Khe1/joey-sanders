from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import httpx

router = APIRouter()
client = httpx.AsyncClient()

from app.database import get_db
from sqlalchemy.orm import Session

from app.utils import tiqets_api

from app.services.produit_services import ProductServices

import math

@router.get("/products")
async def get_products(db: Session = Depends(get_db), page: int = 1, query: str = ''):
    res = {}
    service_prod = ProductServices()
    res_tiqets = await tiqets_api.products(page=page, query=query)
    res['pages'] = {
            'current': page,
            'total': math.ceil(res_tiqets['pagination']['total'] / 10)}
    res['products'] = []
    for r in res_tiqets['products']:
        read_res = service_prod.read_kwargs(db, referenceExterne=r['id'])
        res['products'].append({
            'local_ref': read_res.id if read_res else '',
            'external_ref': r['id'],
            'name': r['title']
        })
    return res