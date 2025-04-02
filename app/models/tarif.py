from sqlalchemy import Column, Integer, Numeric, DateTime, String, Boolean
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Tarif(Base):
    __tablename__ = 'tarifTemp'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    idCodeTarif = Column(Integer, nullable=False) #Why 1
    vente = Column(Boolean, nullable=False)
    date = Column(Integer, nullable=False)
    dateFin = Column(Integer, nullable=True)
    idProduitCategorie = Column(Integer, nullable=False)
    idDevise = Column(Integer, nullable=False, default=403)
    prixBrochure = Column(Numeric(18, 3), nullable=True)
    prixBase = Column(Numeric(18, 3), nullable=True)
    prixEnfant = Column(Numeric(18, 3), nullable=True)
    dateModification = Column(DateTime, nullable=False)
    dateCreation = Column(DateTime, nullable=False)
    canalCreation = Column(String(30), nullable=True)
    jourSemaine = Column(String(7), nullable=True, default='1111111')
    prixBebe = Column(Numeric(18, 3), nullable=True)
    commentaire = Column(String(400), nullable=True)
    idOdoo = Column(Integer, nullable=True)