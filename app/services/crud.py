from typing import Type, TypeVar, Generic, List
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import and_

Base = declarative_base()

ModelType = TypeVar("ModelType", bound=Base)

class CRUD(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.insert_queue = []
        self.update_queue = []
        self.delete_queue = []

    def create(self, session: Session, **kwargs) -> ModelType:
        obj = self.model(**kwargs) 
        session.add(obj) 
        session.commit()
        session.refresh(obj) 
        return obj
    
    def create_all(self, session: Session, data: list) -> List[ModelType]:
        try:
            session.add_all(data)
            session.commit()
            for obj in data:
                session.refresh(obj)
            return data
        except Exception as e:
            print('Exception:', e)
            db.rollback()
            raise e

    def read(self, session: Session, obj_id: int) -> ModelType:
        return session.query(self.model).filter_by(id=obj_id).first()
    
    def read_kwargs(self, session: Session, **kwargs):
        filters = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)
        
        return (
            session
            .query(self.model)
            .order_by(self.model.id)
            .filter(and_(*filters)).first()
        )

    def read_all_kwargs(self, session: Session, skip: int = 0, limit: int = 100, **kwargs) -> ModelType:
        filters = []
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                filters.append(getattr(self.model, key) == value)
        
        return (
            session
            .query(self.model)
            .order_by(self.model.id)
            .filter(and_(*filters))
            .offset(skip).limit(limit).all()
        )

    def read_all(self, session: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        return (
            session
            .query(self.model)
            .order_by(self.model.id)
            .offset(skip).limit(limit).all()
        )

    def update(self, session: Session, id: int, **kwargs) -> ModelType:
        obj = session.query(self.model).filter_by(id=id).first()
        for field, value in kwargs.items():
            if hasattr(obj, field):
                setattr(obj, field, value) 
        session.commit()
        session.refresh(obj)
        return obj
    
    def update_all(self, session: Session, mappings: list):
        try:
            session.bulk_update_mappings(self.model, mappings)
            session.flush()
            session.commit()
        except Exception as e:
            print('Exception:', e)
            db.rollback()
            raise e

    def delete(self, session: Session, obj_id: int) -> ModelType:
        obj = session.query(self.model).filter_by(id=obj_id).first()
        session.delete(obj)
        session.commit()
        return 
    
    
    def delete_all(self, session: Session):
        session.query(self.model).delete()
        session.commit()
        return
    
    def queue_insert(self, session: Session, data: List[ModelType], limit: int = 1000) -> List[ModelType]:
        self.append_insert_queue_list(data)
        print("INSERT QUEUE", self.insert_queue)
        if len(self.insert_queue) >= limit:
            inserted = self.create_all(session, self.insert_queue)
            self.insert_queue = []
            for ins in inserted:
                print(ins)
            return inserted

    def queue_update(self, session: Session, mappings: list, limit: int = 1000):
        self.update_queue = self.update_queue + mappings
        if len(self.update_queue) >= limit:
            ids = [m['id'] for m in self.update_queue]
            self.update_all(session, self.update_queue)
            self.update_queue = []
            return (
                session
                .query(self.model)
                .filter(self.model.id.in_(ids)).all()
            )
    
    def queue_delete(self, session: Session, data: List[ModelType], limit: int = 1000):
        self.append_delete_queue_list(data)
        if len(self.delete_queue) >= limit:
            for obj in self.delete_queue:
                session.delete(obj)
            session.commit()

    # Misc
    def append_insert_queue_kwargs(self, **kwargs) -> List[ModelType]:
        print('APPENDED', self.model(**kwargs))
        self.insert_queue.append(self.model(**kwargs))
        return self.insert_queue
    
    def append_insert_queue_model(self, model: ModelType) -> List[ModelType]:
        self.insert_queue.append(self.model)
        return self.insert_queue
    
    def append_insert_queue_list(self, data: List[ModelType]) -> List[ModelType]:
        self.insert_queue = self.insert_queue + data
        return self.insert_queue

    def append_update_queue(self, mapping: dict) -> List[ModelType]:
        self.update_queue.append(mapping)
        return self.update_queue
    
    def append_delete_queue_kwargs(self, **kwargs) -> List[ModelType]:
        self.delete_queue.append(self.model(**kwargs))
        return self.delete_queue
    
    def append_delete_queue_model(self, model: ModelType) -> List[ModelType]:
        self.delete_queue.append(self.model)
        return self.delete_queue
    
    def append_delete_queue_list(self, data: List[ModelType]) -> List[ModelType]:
        self.delete_queue = self.delete_queue + data
        return self.delete_queue