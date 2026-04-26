import json
import boto3
import os
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

SECRET_ARN = os.getenv("SECRET_ARN")
REGION = "us-east-1"


@lru_cache()
def get_secret():
    client = boto3.client("secretsmanager", region_name=REGION)
    response = client.get_secret_value(SecretId=SECRET_ARN)
    return json.loads(response["SecretString"])


def get_database_url():
    secret = get_secret()

    return (
        f"postgresql+asyncpg://{secret['username']}:{secret['password']}"
        f"@{os.environ['DB_HOST']}:{os.getenv('DB_PORT','5432')}/postgres"
    )


_engine = None
_sessionmaker = None


def get_sessionmaker():
    global _engine, _sessionmaker

    if _sessionmaker is None:
        _engine = create_async_engine(
            get_database_url(),
            pool_size=1,
            max_overflow=0,
            pool_pre_ping=True,
        )

        _sessionmaker = async_sessionmaker(
            bind=_engine,
            expire_on_commit=False,
        )

    return _sessionmaker


async def get_db():
    SessionLocal = get_sessionmaker()
    async with SessionLocal() as session:
        yield session