FROM python:3.12.8-slim AS builder

# Create app directory
WORKDIR /app
RUN apt-get update && \
    apt-get install -y
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"
RUN python -m pip install --upgrade pip

COPY requirements.txt /app
RUN pip install --no-cache-dir -r requirements.txt


FROM python:3.12.8-slim AS runner

WORKDIR /app
COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY ./app ./

ARG POSTGRES_HOST
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_DATABASE

ARG SECRET_KEY
ARG JWT_SIGNING_ALGORITHM
ARG ACCESS_TOKEN_EXPIRE_MINUTES

ENV POSTGRES_HOST=${POSTGRES_HOST}
ENV POSTGRES_USER=${POSTGRES_USER}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ENV POSTGRES_DATABASE=${POSTGRES_DATABASE}

ENV SECRET_KEY=${SECRET_KEY}
ENV JWT_SIGNING_ALGORITHM=${JWT_SIGNING_ALGORITHM}
ENV ACCESS_TOKEN_EXPIRE_MINUTES=${ACCESS_TOKEN_EXPIRE_MINUTES}

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]