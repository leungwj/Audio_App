# Sytem imports
from typing import Union, Dict, Any, Callable, Tuple

# FastAPI-related imports
from fastapi import status, Response, HTTPException
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import Base

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Extra imports
from uuid import UUID

class BaseRouter:
    @staticmethod
    async def update(
        id: Union[str, UUID],
        cls: Base,
        fields: Dict[str, Any],
        response: Response,
        session: Session,
        validate: Callable[[Session, Base], Tuple[bool, Dict[str, Any]]] = lambda session, obj: (True, None)
    ):
        try:
            # ensure all form fields do not have leading or trailing whitespaces
            fields = {key: value.strip() if isinstance(value, str) else value for key, value in fields.items()}

            obj = cls(
                id=id,
                **fields
            )

            success, res = validate(session=session, obj=obj)
            
            if not success:
                raise Exception(res.get("error"))

            success, res = Postgres_DB.update(session=session, updated_obj=obj)

            if not success:
                raise Exception(res.get("error"))

            return {
                "id": res.get("id"),
                "updated_at": res.get("updated_at")
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
                detail=str(e)
            )

    @staticmethod
    async def delete(
        id: Union[str, UUID],
        cls: Base,
        response: Response,
        session: Session
    ):
        try:
            success, res = Postgres_DB.retrieve(session=session, tbl=cls, value=id)

            if not success:
                raise Exception(res.get("error"))
            elif len(res.get("objs")) == 0:
                response.status_code = status.HTTP_404_NOT_FOUND
                raise Exception(f"No objects with {id} found")

            obj = res.get("objs")[0]

            success, res = Postgres_DB.delete(session=session, obj=obj)

            if not success:
                raise Exception(res.get("error"))

            return {
                "id": res.get("id"),
                "deleted_at": res.get("deleted_at")
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
                detail=str(e)
            )

    @staticmethod
    async def retrieve(
        id: Union[str, UUID],
        cls: Base,
        scheme: BaseModel,
        response: Response,
        session: Session
    ):
        try:
            success, res = Postgres_DB.retrieve(session=session, tbl=cls, value=id)

            if not success:
                raise Exception(res.get("error"))
            elif len(res.get("objs")) == 0:
                response.status_code = status.HTTP_404_NOT_FOUND
                raise Exception(f"No objects with {id} found")

            obj = res.get("objs")[0]
            obj_json = scheme.model_validate(obj).model_dump_json()

            return {
                "obj": obj_json,
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
                detail=str(e)
            )
    
    @staticmethod
    async def create(
        cls: BaseModel,
        fields: Dict[str, Any],
        response: Response,
        session: Session,
        validate: Callable[[Session, Base], Tuple[bool, Dict[str, Any]]] = lambda session, obj: (True, None)
    ):
        try:
            fields = {key: value.strip() if isinstance(value, str) else value for key, value in fields.items()}

            obj = cls(
                **fields
            )

            success, res = validate(session=session, obj=obj)
            
            if not success:
                raise Exception(res.get("error"))

            success, res = Postgres_DB.insert(session=session, obj=obj)

            if not success:
                raise Exception(res.get("error"))

            return {
                "id": res.get("id"),
                "created_at": res.get("created_at")
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
                detail=str(e)
            )

    @staticmethod
    async def retrieve_all(
        cls: Base,
        scheme: BaseModel,
        response: Response,
        session: Session
    ):
        try:
            success, res = Postgres_DB.retrieve(session=session, tbl=cls)

            if not success:
                raise Exception(res.get("error"))

            objs = res.get("objs")
            objs_json = [scheme.model_validate(obj).model_dump_json() for obj in objs]

            return {
                "objs": objs_json,
                "error": ""
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
                detail=str(e)
            )