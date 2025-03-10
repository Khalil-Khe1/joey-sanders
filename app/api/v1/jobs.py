from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

import httpx
import datetime

from app.config import settings
from app.database import get_db
from app.services import categorie_services, produit_services, tarif_services
from app.utils import tarif_utils

from sqlalchemy.orm import Session

from collections import namedtuple

router = APIRouter()
client = httpx.AsyncClient()

@router.get('/availability')
async def availability(product_id : int, db : Session = Depends(get_db)):
    if product_id is None:
        return {'Error': 'Product ID not sepcified'}

    ref_produit = product_id
    list_categories = []
    list_tarifs = []

    ref_produit = ref_produit[0].replace('p', '')

    headers = {
        'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
        'User-Agent': 'FastAPI/1.0',
        'Accept': 'application/json',
    }

    query_params = {
        'lang': 'fr',
        'currency': 'EUR'
    }
    try:
        response = await client.get(
            f'https://api.tiqets.com/v2/products/{ref_produit}/product-variants', 
            headers=headers, 
            params=query_params
        )
        response.raise_for_status()
        response = response.json()
    except httpx.HTTPStatusError as e:
        return {'Error': f'{e.response.status_code} - {e.response.text}'}

    groups = response['groups']
    variants = response['variants']

    response = await client.get(
        f'https://api.tiqets.com/v2/products/{ref_produit}/availability', 
        headers=headers, 
        params=query_params
    )
    response.raise_for_status()
    response = response.json()

    dates = response['dates']

    categories = []

    for date in dates:
        for timeslot in date['timeslots']:
            tarifs = tarif_utils.create_category(
                variants,
                groups,
                timeslot['time'],
                timeslot['timezone'],
                date['date'],
                timeslot['variants']
            )
            if not tarifs:
                continue
            categories.append(tarifs)
    list_tarifs = list_tarifs + tarif_utils.clean_categories(categories)
    local_categs = []
    for item in list_tarifs:
        local_categs.append(f'{item["categorie"]}{" - " + item["temps"] if item["temps"] != "whole_day" else ""}')
    list_categories = list(set(list_categories + local_categs))
    print(ref_produit)

    return {'id': ref_produit, 'categories': list_categories, "tarifs": list_tarifs}

@router.get('/availability-all')
async def availability_all(db : Session = Depends(get_db)):
    list_results = []

    ref_list = produit_services.get_all_remote_id(db)
    for i, ref in enumerate(ref_list):
        list_results.append(await availability(ref, db))
    
    return list_results

@router.post('/create-all-categories')
async def create_all_categories(db : Session = Depends(get_db)):
    list_categories = await availability_all(db)
    list_categories = list(filter(lambda e: 'Error' not in e.keys(), list_categories))
    for item in list_categories:
        for categ in item['categories']:
            new_categ = categorie_services.create(
                db,
                idProduit=int(item['id']),
                nomCategorie=categ,
                trajetSimple=1,
                suspendu=0
                )
    return {'Success': 'True'}

@router.post('/create-all-tarifs')
async def create_all_tarifs(db : Session = Depends(get_db)):
    list_availablity = await availability_all(db)
    list_availablity = list(filter(lambda e: 'Error' not in e.keys(), list_availablity))
    for item in list_availablity:
        for tarif in item['tarifs']:
            category_name = f'{tarif["categorie"]} - {tarif["temps"] if tarif["temps"] != "whole_day" else ""}'
            category = categorie_services.get_item(db, idProduit=item['id'], nomCategorie=category_name)
            if category is None: #Handle not found
                continue
            
            index = [0, 1]
            prices = [
                [tarif['achat_adulte'], tarif['achat_enfant']], 
                [tarif['recommande_adulte'], tarif['recommande_enfant']]
            ]
            for i in index: 
                new_tarif = tarif_services.create(
                    db,
                    idProduitCategorie=int(category.id),
                    idCodeTarif=1,
                    date=int(tarif['date_debut'].replace('-', '')),
                    dateFin=int(tarif['date_fin'].replace('-', '')),
                    vente=i,
                    idDevise=403, # 403 = EUR
                    dateCreation=datetime.datetime.now(),
                    dateModification=datetime.datetime.now(),
                    prixBase=prices[i][0],
                    prixEnfant=prices[i][1]
                    )
    return {'Success': 'True'}

@router.put('/find-group')
async def find_group(db : Session = Depends(get_db)):
    ref_list = produit_services.get_all_remote_id(db)

    for ref_produit in ref_list:
        ref_produit = ref_produit[0].replace('p', '')
        if(ref_produit == ''):
            print(f'empty')
            continue
        else:
            headers = {
                'Authorization': 'Token OmpSeEXpj5jITovEfjslUzxAx8r7Vt61',
                'User-Agent': 'FastAPI/1.0',
                'Accept': 'application/json',
            }

            query_params = {
                'lang': 'fr',
                'currency': 'EUR'
            }

            print('ref:',ref_produit)
            response = await client.get(
                f'https://api.tiqets.com/v2/products/{ref_produit}/product-variants', 
                headers=headers, 
                params=query_params
            )
            response.raise_for_status()
            response = response.json()

            variants = response['variants']
            for variant in variants:
                if(len(variant['group_ids']) > 1):
                    return {'product id': ref_produit}

