from sqlalchemy.orm import Session
from app.models.produit import Produit

def get_item(db : Session, item_id : int):
    return db.query(Produit).filter(Produit.id == item_id).first()

def get_all(db: Session):
    return (
        db
        .query(Produit)
        .filter(Produit.idFournisseur == 778)
        .limit(5)
        .all()
    )
    #.with_entities(Produit.id, Produit.referenceExterne, Produit.nom, Produit.nomEN, Produit.description)

def get_all_nominit(db : Session):
    return (
        db
        .query(Produit)
        .filter(Produit.idFournisseur == 778)
        .with_entities(Produit.id, Produit.nomInitial)
        .limit(5)
        .all()
    )

def get_remote_id(db : Session, item_id : int):
    return (
        db
        .query(Produit)
        .filter(Produit.id == item_id)
        .with_entities(Produit.referenceExterne)
        .first()
    )

def get_all_remote_id(db : Session):
    return(
        db
        .query(Produit)
        .filter(Produit.idFournisseur == 778)
        .with_entities(Produit.referenceExterne)
        .limit(1)
        .all()
    )
