from sqlalchemy.orm import Session

from app.models.produit import Produit
from app.services.crud import CRUD

from app.utils import tiqets_api

from app.utils.constants import PRODUCT_COMPARE

class ProductServices(CRUD):
    def __init__(self):
        self.model = Produit
        self.insert_queue = []
        self.update_queue = []
        self.delete_queue = []

    def get_all_nominit(db: Session):
        return (
            db
            .query(Produit)
            .filter(Produit.idFournisseur == 778)
            .with_entities(Produit.id, Produit.nomInitial)
            .limit(5)
            .all()
        )

    def get_all_remote_id(db: Session):
        return(
            db
            .query(Produit)
            .filter(Produit.idFournisseur == 778)
            #.with_entities(Produit.referenceExterne)
            .limit(20)
            .all()
        )
    
    def bulk_insert(self, db: Session, list_products: list):
        limit = 10 # Change to 1000
        insert_queue = []
        for product in list_products:
            insert_queue.append(Produit(
                nom=product['title'],
                nomInitial=product['title'],
                description=product['summary'],
                referenceExterne=product['id']
            ))
        return self.queue_insert(db, insert_queue, limit) 

    async def bulk_update(self, db: Session):
        skip = 0
        limit = 10 # Change 10 to 1000
        self.update_queue = []
        while self.read_all(db, skip=skip, limit=1):
            list_prod = self.read_all(db, skip=skip, limit=limit) 
            for product in list_prod:
                tiqets_prod = await tiqets_api.product(product.referenceExterne)
                if not tiqets_prod:
                    pass # Tiqets API didn't find the product
                tiqets_prod = tiqets_prod['product']
                if any(getattr(product, key[0]) != tiqets_prod[key[1]] for key in PRODUCT_COMPARE):
                    self.append_update_queue({
                        'id': product.id, 
                        'nomInitial': tiqets_prod['title'], 
                        'description': tiqets_prod['summary'],
                        'dateModification': datetime.utcnow()
                    })
                    if len(self.update_queue) >= limit:
                        self.update_all(db, self.update_queue)
                        self.update_queue = []
            skip = skip + limit
        if len(self.update_queue) > 0:
            self.update_all(db, self.update_queue)
            self.update_queue = []