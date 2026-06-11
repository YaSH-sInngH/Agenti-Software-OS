from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.core.config.settings import settings

# Neon (serverless Postgres) closes idle connections, which leaves stale
# sockets in the pool -> "SSL connection has been closed unexpectedly".
# pool_pre_ping validates (and transparently reconnects) on checkout;
# pool_recycle drops connections older than 5 min; keepalives keep the
# TCP link alive during quiet periods.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    },
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()