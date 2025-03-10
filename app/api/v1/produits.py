from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import httpx

from app.config import settings
from app.database import get_db
from app.services import produit_services, tmp_products_services

from sqlalchemy.orm import Session

from collections import namedtuple

router = APIRouter()
client = httpx.AsyncClient()

@router.post("/")
async def tiqets_products():
    headers = {
        "Authorization": "Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61",
        "User-Agent": "FastAPI/1.0",
        "Accept": "application/json",
    }

    query_params = {
        'sort': 'title asc',
        'lang': 'fr',
        'currency': 'EUR',
        'query': 'burj khalifa'
    }
    
    res = await client.get('https://api.tiqets.com/v2/products', headers=headers, params=query_params)
    res.raise_for_status()
    return res.json()

@router.get("/local")
async def local_products(db : Session = Depends(get_db)):
    products = produit_services.get_all(db)
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'referenceExterne': product.referenceExterne,
            'nom': product.nom,
            'nomEN': product.nomEN,
            'description': product.description
        })
    return {'results': results}

@router.get('/test')
async def test():
    import paddle
    print(paddle.__version__)
    return {'ss': 'ss'}

@router.patch("/update")
async def update_products(db : Session = Depends(get_db)):
    products = tmp_produit_services.get_all_nominit(db)
    print(products)
    results = []
    update_ops = []
    for product in products:
        headers = {
            "Authorization": "Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61",
            "User-Agent": "FastAPI/1.0",
            "Accept": "application/json",
        }
        query_params = {
            'sort': 'title asc',
            'lang': 'fr',
            'currency': 'EUR',
            'query': product.nomInitial
        }
        res = await client.get(
            'https://api.tiqets.com/v2/products',
            headers=headers,
            params=query_params
        )
        res.raise_for_status()
        returned = res.json()
        
        found_product = False
        for ret in returned['products']:
            if(ret['title'] == product.nomInitial):
                print('TROOOOOt')
                print(ret['title'])
                found_product = ret
                break
        if(found_product):
            update_ops.append({
                'id': product.id,
                'referenceExterne': found_product['id']
            })
        else:
            update_ops.append({
                'id': product.id,
                'actif': False
            })
    print(update_ops)
    tmp_produit_services.patch_bulk_update(db, update_ops)
    return {'results': update_ops}