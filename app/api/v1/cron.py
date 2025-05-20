from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
import httpx

from app.config import settings
from app.database import get_db

from sqlalchemy.orm import Session

from collections import namedtuple

router = APIRouter()
client = httpx.AsyncClient()

from app.services.produit_services import ProductServices
from app.services.categorie_services import CategoryServices
from app.services.tarif_services import TarifServices

from app.api.v1 import jobs

from app.utils import tiqets_api
from app.utils.constants import (
    PRODUCT_COMPARE,
    CATEGORY_COMPARE,
    TARIF_COMPARE
)

from app.api.v1 import example

@router.post('/create')
async def create_one(product_ref: str, db: Session = Depends(get_db)):
    #jobs.reset_tables(db)
    service_prod = ProductServices()

    page = 1
    size = 1 # Change size from 1 to 100
    list_products = ['###']
    product_exists = service_prod.read_kwargs(db, referenceExterne=product_ref)
    if product_exists:
        return {'message': 'Product already exists'}
    while len(list_products) > 0:
        list_products = []
        res = await tiqets_api.product(product_ref, 'fr', 'EUR')
        print(res)
        list_products = [res['product']]
        created_products = service_prod.bulk_insert(db, list_products)
        if created_products:
            res = []
            for item in created_products:
                res_availability = await jobs.availability(item.id, item.referenceExterne)
                if res_availability['success'] == 'false':
                    return {'success': 'false'}
                res.append(res_availability)
            await jobs.create_all_categories(res, db)
            await jobs.create_all_tarifs(res, db)  
        page = page + 1
        if page >= 1: # Remove this
            break
    created_products = service_prod.queue_insert(db, [], 1)
    if created_products:
        res = []
        for item in created_products:
            res_availability = await jobs.availability(item.id, item.referenceExterne)
            if res_availability['success'] == 'false':
                return {'success': 'false'}
            res.append(res_availability)
        await jobs.create_all_categories(res, db)
        await jobs.create_all_tarifs(res, db)
    return {'success': 'True'}

""" if res_availability['success'] == 'false':
    return {'success': 'false'}
res.append(res_availability) """

@router.post('/create-all')
async def create_all(db: Session = Depends(get_db)):
    #jobs.reset_tables(db)
    service_prod = ProductServices()

    page = 1
    size = 1 # Change size from 1 to 100
    list_products = ['###']

    while len(list_products) > 0:
        list_products = []
        """ res = await tiqets_api.products('fr', 'EUR', size, page) """
        res = await tiqets_api.product('1087306', 'fr', 'EUR')
        """ list_products = res['products'] """
        list_products = [res['product']]
        created_products = service_prod.bulk_insert(db, list_products)
        if created_products:
            res = []
            for item in created_products:
                res.append(await jobs.availability(item.id, item.referenceExterne))
            await jobs.create_all_categories(res, db)
            await jobs.create_all_tarifs(res, db)  
        page = page + 1
        if page >= 1: # Remove this
            break
    created_products = service_prod.queue_insert(db, [], 1)
    if created_products:
        res = []
        for item in created_products:
            res.append(await jobs.availability(item.id, item.referenceExterne))
        await jobs.create_all_categories(res, db)
        await jobs.create_all_tarifs(res, db)
    return {'success': 'True'}

@router.post('/main')
async def cron_job(db : Session = Depends(get_db)):
    service_prod = ProductServices()
    service_categ = CategoryServices()
    service_tarif = TarifServices()

    await service_prod.bulk_update(db)

    skip, limit = 0, 10 # Change 10 to 1000
    while service_prod.read_all(db, skip=skip, limit=1): # Change read_all to read_all_kwargs and add idFournisseur=778 (Tiqets)
        list_products = service_prod.read_all(db, skip=skip, limit=limit)
        for product in list_products:
            res = await jobs.availability(product.id, product.referenceExterne)
            #res = example.product
            inserted_categs, updated_categs = service_categ.queue_from_availability(db, product.id, res['categories'])
            updated_categs = list(filter(lambda e: e.suspendu == 0, updated_categs)) if updated_categs else [] # Get whitelist
            """ service_tarif.queue_from_categories(
                db, 
                inserted_categs if inserted_categs else [] + updated_categs if updated_categs else [], 
                res['tarifs']
            ) """
            service_categ.queue_insert(db, [], 1)
            service_categ.queue_update(db, [], 1)
            prod_categories = service_categ.read_all_kwargs(db, 0, 100, idProduit=product.id)
            for prod_categ in prod_categories:
                found_tarifs = service_tarif.read_all_kwargs(db, 0, 100, idProduitCategorie=prod_categ.id)
                service_tarif.queue_delete(db, found_tarifs)
            service_tarif.queue_delete(db, [], 1)
            service_tarif.queue_from_categories(db, prod_categories, res['tarifs'])
            del inserted_categs
            del updated_categs
        skip = skip + limit
    service_categ.queue_insert(db, [], 1)
    service_categ.queue_update(db, [], 1)
    service_tarif.queue_insert(db, [], 1)

    return {'success': 'True'}

@router.post('/demo-create')
async def create_one(product_ref: str, db: Session = Depends(get_db)):
    from app.api.v1 import example

    service_prod = ProductServices()

    page = 1
    size = 1 # Change size from 1 to 100
    list_products = ['###']
    product_exists = service_prod.read_kwargs(db, referenceExterne=product_ref)
    if product_exists:
        return {'message': 'Product already exists'}
    while len(list_products) > 0:
        list_products = []
        res = await tiqets_api.product(product_ref, 'fr', 'EUR')
        print(res)
        list_products = [res['product']]
        created_products = service_prod.bulk_insert(db, list_products)
        if created_products:
            res = []
            for item in created_products:
                res_availability = example.body #await jobs.availability(item.id, item.referenceExterne)
                example.body['id'] = item.id
                if res_availability['success'] == 'false':
                    return {'success': 'false'}
                res.append(res_availability)
            await jobs.create_all_categories(res, db)
            await jobs.create_all_tarifs(res, db)  
        page = page + 1
        if page >= 1: # Remove this
            break
    created_products = service_prod.queue_insert(db, [], 1)
    if created_products:
        res = []
        for item in created_products:
            res_availability = example.body #await jobs.availability(item.id, item.referenceExterne)
            example.body['id'] = item.id
            if res_availability['success'] == 'false':
                return {'success': 'false'}
            res.append(res_availability)
        await jobs.create_all_categories(res, db)
        await jobs.create_all_tarifs(res, db)
    return {'success': 'True'}

@router.get('/test')
async def test():
    return {"success": "true"}