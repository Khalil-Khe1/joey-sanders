from sqlalchemy.orm import Session
from app.models.produit_temp import ProduitTemp

def get_item(db: Session, item_id: int):
    return db.query(ProduitTemp).filter(models.Item.id == item_id).first()

def get_all(db: Session):
    return (
        db
        .query(ProduitTemp)
        .filter(ProduitTemp.idFournisseur == 778)
        .limit(5)
        .all()
    )
    #.with_entities(Produit.id, Produit.referenceExterne, Produit.nom, Produit.nomEN, Produit.description)

def get_all_nominit(db : Session):
    return (
        db
        .query(ProduitTemp)
        .filter(ProduitTemp.idFournisseur == 778)
        .with_entities(ProduitTemp.id, ProduitTemp.nomInitial)
        .all()
    )

def patch_bulk_update(db : Session, update_ops):
    db.bulk_update_mappings(ProduitTemp, update_ops)
    db.commit()
    #db.close()
