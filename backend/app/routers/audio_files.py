# Sytem imports
import os
from typing import Union, Annotated, Tuple, Dict, Any
from datetime import datetime, timedelta, timezone

# FastAPI-related imports
from fastapi import APIRouter, Form, status, Response, Depends, HTTPException, UploadFile, File
from app.dependencies import get_session, oauth2_scheme, decode_access_token
from app.postgres.postgres_db import Postgres_DB
from app.postgres.mappings import Audio_File
# from app.routers.base import BaseRouter

# SQLAlchemy-related imports
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict

# azure imports
from azure.storage.blob.aio import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import generate_blob_sas, BlobSasPermissions

# Extra imports
from uuid import UUID
import uuid
from sqlalchemy import and_

router = APIRouter(
    prefix="/audio_files",
    tags=["audio_files"],
    responses={404: {"description": "Not found"}}
)

class AudioFileScheme(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    description: str
    category: str

@router.get("/token/{id}", status_code=status.HTTP_200_OK)
async def generate_sas_blob_url(
    id: UUID,
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    try:
        # retrieve the audio file
        success, res = Postgres_DB.retrieve(session=session, tbl=Audio_File, value=id, col_name="id")

        if not success:
            raise Exception(res.get("error"))

        audio_file = res.get("objs")[0]

        if audio_file.user_id != UUID(user_id):
            raise Exception("You do not have permission to access this audio file")

        # generate a SAS URL for the audio file
        success, res = await generate_sas_blob_url(str(audio_file.blob_name))

        if not success:
            raise Exception(res.get("error"))

        return {
            "audio_id": id,
            "audio_url": res.get("audio_url")
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
            detail=str(e)
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_audio_file(
    description: Annotated[str, Form()],
    category: Annotated[str, Form()],
    audio_file: Annotated[UploadFile, File()],
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    try:
        success, res = await upload_file_to_bucket(audio_file)

        if not success:
            raise Exception(res.get("error"))
        
        blob_name = res.get("blob_name")

        audio_file = Audio_File(
            user_id=UUID(user_id),
            description=description,
            category=category,
            blob_name=UUID(blob_name)
        )

        success, res = Postgres_DB.insert(session=session, obj=audio_file)

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

@router.get("/", status_code=status.HTTP_200_OK)
async def retrieve_all_audio_files(
    response: Response,
    session: Annotated[Session, Depends(get_session)],
    token: Annotated[str, Depends(oauth2_scheme)]
):
    user_id = decode_access_token(token)

    try:
        # retrieve all audio files for the user
        success, res = Postgres_DB.retrieve(session=session, tbl=Audio_File, value=UUID(user_id), col_name="user_id")

        if not success:
            raise Exception(res.get("error"))

        objs = res.get("objs")
        objs_json = [AudioFileScheme.model_validate(obj).model_dump_json() for obj in objs]

        return {
            "objs": objs_json,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR if response.status_code is None else response.status_code,
            detail=str(e)
        )
    
# Helper Functions
# ---------------------------------------------------------------------

async def upload_file_to_bucket(
    audio_file: UploadFile
) -> Tuple[bool, Dict[str, Any]]:
    # file_ext = os.path.splitext(audio_file.filename)[1]
    # blob_name = f"{str(uuid.uuid4())}{file_ext}"
    blob_name = str(uuid.uuid4())
    # content_type = audio_file.content_type

    # https://learn.microsoft.com/en-us/dotnet/api/azure.storage.blobs.blobserviceclient.-ctor?view=azure-dotnet#azure-storage-blobs-blobserviceclient-ctor(system-string)
    blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZ_STORAGE_CONNECTION_STRING"))

    async with blob_service_client:
        container_client: ContainerClient = blob_service_client.get_container_client(os.getenv("AZ_STORAGE_CONTAINER_NAME"))
        try:
            blob_client: BlobClient = container_client.get_blob_client(blob_name)
            audio_data: bytes = await audio_file.read()
            await blob_client.upload_blob(audio_data)
        except Exception as e:
            return False, {
                "error": str(e)
            }
        
    return True, {
        "blob_name": blob_name,
    }

async def generate_sas_blob_url(
    blob_name: str
) -> Tuple[bool, Dict[str, Any]]:
    try:
        blob_service_client = BlobServiceClient.from_connection_string(os.getenv("AZ_STORAGE_CONNECTION_STRING"))

        async with blob_service_client:
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=os.getenv("AZ_STORAGE_CONTAINER_NAME"),
                blob_name=blob_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=datetime.now(timezone.utc)+ timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
            )

            audio_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{os.getenv('AZ_STORAGE_CONTAINER_NAME')}/{blob_name}?{sas_token}"

        return True, {
            "audio_url": audio_url
        }
    except Exception as e:
        return False, {
            "error": str(e)
        }