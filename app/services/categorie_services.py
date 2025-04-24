from sqlalchemy.orm import Session

from app.models.categorie import Categorie
from app.services.crud import CRUD

from sqlalchemy import and_
import datetime

from app.utils import tiqets_api

from app.utils.constants import CATEGORY_COMPARE

class CategoryServices(CRUD):
    def __init__(self):
        self.model = Categorie
        self.insert_queue = []
        self.update_queue = []
        self.delete_queue = []

    def queue_from_availability(self, db: Session, product_id: int, available_categories: list):    
        whitelist, update_queue, insert_queue = [], [], []
        list_categ = self.read_all_kwargs(db, product_id=product_id)
        for categ in list_categ:
            if categ.nomCategorie in available_categories:
                whitelist.append(categ.nomCategorie)
                if categ.suspendu == 1:
                    update_queue.append({
                    'id': categ.id, 
                    'suspendu': 0, 
                    'dateModification': datetime.datetime.now()
                })
            else:
                update_queue.append({
                    'id': categ.id, 
                    'suspendu': 1, 
                    'dateModification': datetime.datetime.now()
                })
        new = list(set(available_categories) - set(whitelist))
        for item in new:
            insert_queue.append(Categorie(
                idProduit=product_id, 
                nomCategorie=item
            ))
        limit = 10 # Change 10 to 1000
        limit = limit if len(self.insert_queue + self.update_queue) < limit else 1
        inserted = self.queue_insert(db, insert_queue, limit)
        updated = self.queue_update(db, update_queue, limit)
        return inserted, updated
