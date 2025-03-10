from pydantic import BaseModel

class ProduitSchema(BaseModel):
    id: int
    referenceExterne: int
    nom: str
    nomInitial: str

    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dictionaries

    """ [id]
	,[referenceExterne]
    ,[nom]
    ,[nomEN]
    ,[nomInitial]
    ,[description]
    ,[typeProduit]
    ,[vendable]
    ,[idFournisseur]
    ,[prixAppel]
    ,[prixAppelAchat]
    ,[tauxTVA] """