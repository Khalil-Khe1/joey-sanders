from sqlalchemy.orm import Session
from app.services.crud import CRUD

from app.models.tarif import Tarif

import datetime

class TarifServices(CRUD):
    def __init__(self):
        self.model = Tarif
        self.insert_queue = []
        self.update_queue = []
        self.delete_queue = []

    def bulk_insert_from_categories(self, db: Session):
        pass

    def queue_from_categories(self, db: Session, categories: list, available_tarifs: list):
        print(len(categories))
        limit = 10 # Change 10 to 1000
        index = [0, 1]
        insert_queue = []
        for tarif in available_tarifs:
            formatted_name = f'{tarif["categorie"]}{" - " + tarif["temps"] if tarif["temps"] != "whole_day" else ""}'
            for categ in categories:
                if categ.nomCategorie == formatted_name:
                #if categ == formatted_name:
                    prices = [
                        [tarif['achat_adulte'], tarif['achat_enfant']], 
                        [tarif['recommande_adulte'], tarif['recommande_enfant']]
                    ]
                    for i in index:
                        print('new_tarif')
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
