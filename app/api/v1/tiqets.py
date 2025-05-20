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
async def get_products(
    db: Session = Depends(get_db), 
    external_ref: str = '',
    page: int = 1, 
    query: str = '',
    country: str = '',
    imported: bool = False): # False is not imported
    res = {}
    res['pages'] = {
        'current': page,
        'total': 0
    }
    res['products'] = []
    service_prod = ProductServices()
    if external_ref != '':
        res_tiqets = await tiqets_api.product(product_id=external_ref)
        res_tiqets = res_tiqets['product']
        read_res = service_prod.read_kwargs(db, referenceExterne=res_tiqets['id'])
        res['pages'] = {'current': 1, 'total': 1}
        res['products'].append({
            'local_ref': read_res.id if read_res else '',
            'external_ref': external_ref,
            'name': res_tiqets['title']
        })
        return res
    elif imported:
        pass
    else:
        res_tiqets = {
            'products': []
        }
        init_state = True
        country = country.split(';')
        if country[0] == 'country':
            country = country[1]
            city = ''
        elif country[0] == 'city':
            city = country[1]
            country = ''
        else:
            city = ''
            country = ''
        res_tiqets = await tiqets_api.products(page=page, query=query, country=country, city=city)
        while True and len(res_tiqets['products']) != 0:
            res['pages']['total'] = math.ceil(res_tiqets['pagination']['total'] / 10)
            res['products'] = []
            for r in res_tiqets['products']:
                read_res = service_prod.read_kwargs(db, referenceExterne=r['id']) 
                res['products'].append({
                    'local_ref': read_res.id if read_res else '',
                    'external_ref': r['id'],
                    'name': r['title']
                })
                if len(res['products']) >= 10 or len(res_tiqets['products']) < 10:
                    return res
            init_state = False
            page = page + 1
            res_tiqets = await tiqets_api.products(page=page, query=query, country=country, city=city)
    return {
        'pages' : {'total': 0, 'current': 0},
        'products': []
    }