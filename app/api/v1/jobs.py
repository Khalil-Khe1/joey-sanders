from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import httpx
import datetime

from app.config import settings
from app.database import get_db

from app.services.produit_services import ProductServices
from app.services.categorie_services import CategoryServices
from app.services.tarif_services import TarifServices

from app.utils import (
    tarif_utils, 
    tiqets_api
)

from sqlalchemy.orm import Session

from collections import namedtuple

router = APIRouter()
client = httpx.AsyncClient()

@router.get('/availability')
async def availability(id_produit: int, ref_prod: str):
    if ref_prod is None:
        return {'Error': 'Product ID not sepcified'}

    print('AVAILABILITY BEGIN', ref_prod)
    list_categories = []
    list_tarifs = []

    ref_prod = ref_prod.replace('p', '')
    ref_prod = ref_prod.replace('b', '')
    ref_prod = ref_prod.replace(' ', '')

    response = await tiqets_api.variants(ref_prod)
    if 'Error' in response.keys():
        return {'success': 'false'}
    groups = response['groups']
    variants = response['variants']

    response = await tiqets_api.availability(ref_prod)
    if 'Error' in response.keys():
        return {'success': 'false'}
    dates = response['dates']

    list_tarifs = tarif_utils.tarif_workflow(groups, variants, dates)
    list_categories = tarif_utils.extract_categories(list_tarifs)
    print('AVAILABILITY END', ref_prod)

    return {'success': 'true', 'id': id_produit, 'categories': list_categories, "tarifs": list_tarifs}

@router.get('/availability-all')
async def availability_all():
    import random
    from datetime import datetime
    random.seed(datetime.now().timestamp())

    list_results = []

    service_prod = ProductServices()
    ref_list = service_prod.get_all_remote_id(db)
    #ref_list = random.sample(ref_list, 20)
    admitted = []
    for i, ref in enumerate(ref_list):
        id_produit = ref.id
        ref_prod: str = ref.referenceExterne
        ref_prod = ref_prod.replace('p', '')
        ref_prod = ref_prod.replace('b', '')
        ref_prod = ref_prod.replace(' ', '')
        if ref[0] not in admitted:
            list_results.append(await availability(id_produit, ref_prod, db))
            admitted.append(ref_prod)
            if len(admitted) > 5:
                break
    
    return list_results

@router.post('/create-all-categories')
async def create_all_categories(db: Session = Depends(get_db)):
    service_categ = CategoryServices()

    list_categories = await availability_all()
    list_categories = list(filter(lambda e: 'Error' not in e.keys(), list_categories))
    for item in list_categories:
        for categ in item['categories']:
            service_categ.append_insert_queue_kwargs(
                idProduit=int(item['id']),
                nomCategorie=categ
            )
    db.add_all(service_categ.insert_queue)
    db.commit()
    return {'Success': 'True'}

@router.post('/create-all-categories/cron')
async def create_all_categories(data: list, db: Session = Depends(get_db)):
    service_categ = CategoryServices()

    for item in data:
        for categ in item['categories']:
            service_categ.append_insert_queue_kwargs(
                idProduit=int(item['id']),
                nomCategorie=categ
            )
    service_categ.queue_insert(db, [], 1)
    return {'success': 'True'}

@router.post('/create-all-tarifs')
async def create_all_tarifs(db: Session = Depends(get_db)):
    data = await availability_all()
    data = list(filter(lambda e: 'Error' not in e.keys(), data))
    data = []
    for item in data:
        for tarif in item['tarifs']:
            category_name = f'{tarif["categorie"]}{" - " + tarif["temps"] if tarif["temps"] != "whole_day" else ""}'
            service_categ = CategoryServices()
            category = service_categ.read_kwargs(db, idProduit=item['id'], nomCategorie=category_name)
            if category is None: #Handle not found
                continue
            
            index = [0, 1]
            prices = [
                [tarif['achat_adulte'], tarif['achat_enfant']], 
                [tarif['recommande_adulte'], tarif['recommande_enfant']]
            ]
            for i in index: 
                data.append(Tarif(
                    idProduitCategorie=int(category.id),
                    idCodeTarif=1,
                    date=int(tarif['date_debut'].replace('-', '')),
                    dateFin=int(tarif['date_fin'].replace('-', '')),
                    vente=i,
                    dateCreation=datetime.datetime.now(),
                    dateModification=datetime.datetime.now(),
                    prixBase=prices[i][0],
                    prixEnfant=prices[i][1]
                ))
    db.add_all(data)
    db.commit()
    return {'success': 'True'}

@router.post('/create-all-tarifs/cron')
async def create_all_tarifs(data: list, db: Session = Depends(get_db)):
    service_tarif = TarifServices()
    data = list(filter(lambda e: 'Error' not in e.keys(), data))
    for item in data:
        for tarif in item['tarifs']:
            category_name = f'{tarif["categorie"]}{" - " + tarif["temps"] if tarif["temps"] != "whole_day" else ""}'
            service_categ = CategoryServices()
            category = service_categ.read_kwargs(db, idProduit=item['id'], nomCategorie=category_name)
            if category is None: #Handle not found
                continue
            print('CREATE TARIF CATEG ID', category.id)
            index = [0, 1]
            prices = [
                [tarif['achat_adulte'], tarif['achat_enfant']], 
                [tarif['recommande_adulte'], tarif['recommande_enfant']]
            ]
            for i in index: 
                service_tarif.append_insert_queue_kwargs(
                    idProduitCategorie=int(category.id),
                    idCodeTarif=1,
                    date=int(tarif['date_debut'].replace('-', '')),
                    dateFin=int(tarif['date_fin'].replace('-', '')),
                    vente=i,
                    dateCreation=datetime.datetime.now(),
                    dateModification=datetime.datetime.now(),
                    prixBase=prices[i][0],
                    prixEnfant=prices[i][1]
                )
    service_tarif.queue_insert(db, [], 1)
    return {'success': 'True'}

@router.delete('/reset')
def reset_tables(db: Session = Depends(get_db)):
    service = CategoryServices()
    service.delete_all(db)
    service = TarifServices()
    service.delete_all(db)
    service = ProductServices()
    service.delete_all(db)
    return {'success': 'True'}

@router.put('/find-group')
async def find_group(db: Session = Depends(get_db)):
    service_prod = ProductServices()
    ref_list = service_prod.read_all_remote_id(db)

    for ref_prod in ref_list:
        ref_prod = ref_prod[0].replace('p', '')
        if(ref_prod == ''):
            print(f'empty')
            continue
        else:
            response = await tiqets_api.variants(ref_prod)
            variants = response['variants']
            for variant in variants:
                if(len(variant['group_ids']) > 1):
                    return {'product id': ref_prod}