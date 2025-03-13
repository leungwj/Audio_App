# System imports
from typing import Union, Annotated, Tuple, Dict, Any

# required imports
from sqlalchemy import Engine, Connection, select, text, Column
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.postgres.utils import unix_timestamp
from app.postgres.mappings import Base

# QoL imports
from typing import Type, List, Dict, Tuple

# extra imports for testing
from datetime import date

# Postgres DB Class
class Postgres_DB:
    @staticmethod
    def test_connection(engine: Engine) -> bool:
        try:
            conn: Connection = engine.connect()
            print(f"[*] (Postgres) Connection Successful!")
            results = conn.execute(text('SELECT version()')).fetchone()
            print(f"[*] (Postgres) Current Version: {results[0]}")
            conn.close()
            return True
        except Exception as e:
            print(f"[!] (Postgres) Connection Failure: {str(e)}")
            return False

    @staticmethod
    def create_all_tables(engine: Engine, overwrite=False):
        try:
            if overwrite:
                if not Postgres_DB.drop_all_tables(engine=engine):
                    # drop tables failure
                    return False
            Base.metadata.create_all(engine)
            return True
        except (SQLAlchemyError, Exception) as e:
            print(f"[!] (Postgres) Failed to create tables: {e}")
            return False

    @staticmethod
    def drop_all_tables(engine: Engine):
        try:
            Base.metadata.drop_all(engine)
            return True
        except SQLAlchemyError as e:
            print(f"[!] (Postgres) Failed to drop tables: {e}")
            return False

    @staticmethod
    def retrieve(session: Session, tbl: Type[Base], value = None, col_name: str = "id") -> Tuple[bool, Dict[str, Any]]:
        try:
            # select * by default
            statement = select(tbl)

            if value is not None:
                col = getattr(tbl, col_name)
                if col is None:
                    raise Exception(f"Column {col_name} does not exist in {tbl.__name__}.")
                statement = select(tbl).where(col == value)
            
            # this is list of rows, so we need to convert it into objects first
            res = session.execute(statement)
            
            # converts the rows into classes/scalars
            return True, {
                'objs': res.scalars().all()
            }
        except (SQLAlchemyError, Exception) as e:
            print(f"[!] (Postgres) Failed to retrieve {tbl}: {e}")
            return False, {
                'error': str(e)
            }

    @staticmethod
    def insert(session: Session, obj: Base, pk_constraint: bool = False, fk_constraint: bool = False) -> Tuple[bool, Dict[str, Any]]:
        try:
            # session.begin()
            if pk_constraint and obj.id is not None:
                # this is to check if the primary key already exists
                success, res = Postgres_DB.retrieve(session=session, tbl=obj.__class__, value=obj.id)
                if not success:
                    raise Exception(f"Retrieval error: {res.get('error')}")
                elif len(res.get('objs')) > 0:
                    raise Exception(f"{obj.id} already exists.")
            if fk_constraint:
                for relationship in obj.__mapper__.relationships:
                    # for each column affected by the relationship
                    # e.g., Column('id', CHAR(length=11), table=<jobs>, primary_key=True, nullable=False)
                    # e.g., Column('image_id', Uuid(), ForeignKey('pfib_images.id'), table=<dd_inferences>, nullable=False)
                    for col in relationship.local_columns:
                        # first check if it contains any foreign key references
                        # if it does not, means that this is a parent of the relationship, so we ignore
                        if len(col.foreign_keys) > 0:
                            # get the id of the foreign key (e.g., job_id's value)
                            fk_id = getattr(obj, col.name)
                            if fk_id is None:
                                raise Exception(f"Column {col.name} does not exist in {obj.__tablename__}.")
                            
                            # this is the parent's class definition
                            parent_class = relationship.mapper.class_
                            success, res = Postgres_DB.retrieve(session=session, tbl=parent_class, value=fk_id)
                            if not success:
                                raise Exception(f"Retrieval error: {res.get('error')}")
                            elif len(res.get('objs')) == 0:
                                raise Exception(f"Referential integrity violation: {parent_class.__name__} with id={fk_id} does not exist.")

            obj.created_at = unix_timestamp()
            session.add(obj)
        except (SQLAlchemyError, Exception) as e:
            session.rollback()
            print(f"[!] (Postgres) Failed to insert {obj}: {e}")
            return False, {
                'error': str(e)
            }
        else:
            session.commit()
            print(f"[*] (Postgres) Successfully inserted {obj}!")
            return True, {
                'id': obj.id,
                'created_at': obj.created_at
            }

    @staticmethod
    def update(session: Session, updated_obj: Base) -> Tuple[bool, Dict[str, Any]]:
        try:
            # session.begin()
            delta = False
            success, res = Postgres_DB.retrieve(session=session, tbl=updated_obj.__class__, value=updated_obj.id)
            
            if not success:
                raise Exception(f"Retrieval error: {res.get('error')}")
            elif len(res.get('objs')) == 0:
                raise Exception(f"{updated_obj.id} does not exist.")
            obj = res.get('objs')[0]

            for col in obj.__mapper__.columns:
                # do not update foreign key values, as well as created_at, updated_at, deleted_at
                if len(col.foreign_keys) > 0 or col.name in ["created_at", "updated_at", "deleted_at"]:
                    continue

                col_name = col.name
                curr_value = getattr(obj, col_name)
                new_value = getattr(updated_obj, col_name)

                if new_value is None:
                    nullable = getattr(col, "nullable")
                    if not nullable:
                        new_value = curr_value

                if curr_value != new_value:
                    setattr(obj, col_name, new_value)
                    delta = True
            
            if not delta:
                raise Exception(f"No changes detected in {obj}.")
            
            obj.updated_at = unix_timestamp()
            session.add(obj)
        except (SQLAlchemyError, Exception) as e:
            session.rollback()
            print(f"[!] (Postgres) Failed to update {obj}: {e}")
            return False, {
                'error': str(e)
            }
        else:
            session.commit()
            print(f"[*] (Postgres) Successfully updated {obj}!")
            return True, {
                'id': obj.id,
                'updated_at': obj.updated_at
            }

    @staticmethod
    def delete(session: Session, obj: Base, fk_constraint: bool = False, soft_delete = False) -> Tuple[bool, Dict[str, Any]]:
        try:
            # session.begin()
            if fk_constraint:
                # Goal: Check if there are any child objects that still reference this object

                # Step 1: Determine if i'm the parent of any relationship (works by checking if the relationship is PK)
                for relationship in obj.__mapper__.relationships:
                    for col in relationship.local_columns:
                        is_pk = getattr(col, 'primary_key')

                        # if im the parent of any relationship, then get my pk's value
                        if is_pk:
                            pk_id = getattr(obj, col.name)
                            if pk_id is None:
                                raise Exception(f"Column {col.name} does not exist in {obj.__tablename__}.")
                            
                            # Step 2: Determine if there are any child objects that still reference me, this is done by searching my pk's value on the child's fk column
                            child_tbl = relationship.mapper.class_
                            child_col_name = None

                            # get the list of foreign keys that is related to this relationship
                            for fk_col in relationship._calculated_foreign_keys:
                                # for each foreign key, check if the parent col name is matching
                                for fk in fk_col.foreign_keys:
                                    # parent col name is matching
                                    # fk -> ForeignKey('jobs.id'), fk.target_fullname: 'jobs.id', fk_col.name: 'job_id'
                                    if fk.target_fullname == f"{obj.__tablename__}.{col.name}":
                                        child_col_name = fk_col.name
                                        break

                            if child_col_name is None:
                                raise Exception(f"Unable to find matching foreign key column for {col.name} in {relationship}")
                            
                            success, res = Postgres_DB.retrieve(session=session, tbl=child_tbl, value=pk_id, col_name=child_col_name)
                            
                            if not success:
                                raise Exception(f"Retrieval error: {res.get('error')}")
                            # res = child objects
                            elif len(res["objs"]) > 0:
                                raise Exception(f"Referential integrity violation: {len(res["objs"])} references still exists in {child_tbl.__name__}.")
            obj.deleted_at = unix_timestamp()
            if soft_delete:
                session.add(obj)
            else:
                id = obj.id
                deleted_at = obj.deleted_at
                session.delete(obj)
        except (SQLAlchemyError, Exception) as e:
            session.rollback()
            print(f"[!] (Postgres) Failed to delete {obj}: {e}")
            return False, {
                'error': str(e)
            }
        else:
            session.commit()
            print(f"[*] (Postgres) Successfully deleted {obj}!")
            return True, {
                'id': obj.id if soft_delete else id,
                'deleted_at': obj.deleted_at if soft_delete else deleted_at
            }