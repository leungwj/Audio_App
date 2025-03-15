# Audio_App

# Environment Variables (Backend)
POSTGRES_PASSWORD=example
POSTGRES_USER=postgres
POSTGRES_DATABASE=postgres
POSTGRES_HOST=db

SECRET_KEY=2fe00b4f741c2e3bdef9543c775fa8a6f3dc4e3361bdde8ea5f7df7ab8c80a16
JWT_SIGNING_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

AZ_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=audioapp;AccountKey=m6kA4RdIvyY6PGxGnFUaxx0EqNoUfAMbeP/TGdsAYOMqxvl9TIlXvkBR4z5UJjz4Lp29Z4qEe7W++AStANbHLw==;EndpointSuffix=core.windows.net"
AZ_STORAGE_CONTAINER_NAME=audiofiles

# Environment Variables (Frontend)
API_SERVER=http://backend:8000
