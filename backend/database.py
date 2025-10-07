
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import os, ssl

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://neondb_owner:npg_m2fSGCYi9zcB@ep-old-leaf-a116j6wt-pooler.ap-southeast-1.aws.neon.tech/neondb")

# Create SSL context for NeonDB (required for most serverless Postgres)
ssl_context = ssl.create_default_context()

engine = create_async_engine(
	DATABASE_URL,
	echo=True,
	future=True,
	connect_args={"ssl": ssl_context}
)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()
