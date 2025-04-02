from sqlalchemy.orm import Session
from app.services.crud import CRUD

from app.models.tarif import Tarif

import datetime

class TarifServices(CRUD):
    def __init__(self):
        self.model = Tarif
        self.insert_queue = []
        self.update_queue = []

    def bulk_insert_from_categories(self, db: Session):
        pass

    def queue_from_categories(self, db: Session, categories: list, available_tarifs: list):
        limit = 10 # Change 10 to 1000
        index = [0, 1]
        insert_queue = []
        for tarif in available_tarifs:
            if any(categ.nomCategorie == tarif['categorie'] for categ in categories):
                prices = [
                    [tarif['achat_adulte'], tarif['achat_enfant']], 
                    [tarif['recommande_adulte'], tarif['recommande_enfant']]
                ]
                for i in index:
                    insert_queue.append(Tarif(
                        idProduitCategorie=int(categ.id),
                        idCodeTarif=1,
                        date=int(tarif['date_debut'].replace('-', '')),
                        dateFin=int(tarif['date_fin'].replace('-', '')),
                        vente=i,
                        dateCreation=datetime.datetime.now(),
                        dateModification=datetime.datetime.now(),
                        prixBase=prices[i][0],
                        prixEnfant=prices[i][1]
                    ))
        self.queue_insert(db, insert_queue, limit)
