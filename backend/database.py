import json
import boto3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from functools import lru_cache

SECRET_ARN = "arn:aws:secretsmanager:us-east-1:310817946106:secret:rds!db-5a86cdd6-3cee-4905-be2a-a6890658843b-OkgwTk"
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
        f"@{secret['host']}:{secret['port']}/{secret['dbname']}"
    )

engine = create_async_engine(
    get_database_url(),
    pool_size=1,
    max_overflow=0,
    pool_pre_ping=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session