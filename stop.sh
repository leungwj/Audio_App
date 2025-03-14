#!/bin/bash
docker compose down
docker rmi audio_app-frontend:latest
docker rmi audio_app-backend:latest
#docker image prune -f