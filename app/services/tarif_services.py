from sqlalchemy.orm import Session
from app.models.tarif import Tarif

def create(session: Session, **kwargs):
    tarif = Tarif(**kwargs)
    session.add(tarif)
    session.commit()
    session.refresh(tarif) 
    return tarif

def update(session: Session, tarif_id: int, **kwargs):
    tarif = session.query(Tarif).filter_by(id=tarif_id).first()
    if not tarif:
        return None
    for key, value in kwargs.items():
        if hasattr(tarif, key):
            setattr(tarif, key, value)
    tarif.dateModification = datetime.utcnow()
    session.commit()
    session.refresh(tarif)
    return tarif