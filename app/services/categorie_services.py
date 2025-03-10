from sqlalchemy.orm import Session
from app.models.categorie import Categorie
from sqlalchemy import and_

def get_item(db, **kwargs):
    filters = []
    for key, value in kwargs.items():
        if hasattr(Categorie, key):
            filters.append(getattr(Categorie, key) == value)

    return db.query(Categorie).filter(and_(*filters)).first()

""" def get_item(db: Session, idProduit : int, nomCategorie: str):
    return db.query(Categorie).filter """

def get_all(db: Session):
    return (
        db
        .query(Categorie)
        .limit(5)
        .all()
    )
    #.with_entities(Categorie.id, Categorie.referenceExterne, Categorie.nom, Categorie.nomEN, Categorie.description)

def get_all_fields(db : Session):
    return (
        db
        .query(Categorie)
        .filter(Categorie.idFournisseur == 778)
        .with_entities(Categorie.id)
        .limit(5)
        .all()
    )

def create(session: Session, **kwargs):
    categorie = Categorie(**kwargs)
    session.add(categorie)
    session.commit()
    session.refresh(categorie) 
    return categorie

def update(session: Session, categorie_id: int, **kwargs):
    categorie = session.query(Categorie).filter_by(id=categorie_id).first()
    if not categorie:
        return None
    for key, value in kwargs.items():
        if hasattr(categorie, key):
            setattr(categorie, key, value)
    categorie.dateModification = datetime.utcnow()
    session.commit()
    session.refresh(categorie)
    return categorie
