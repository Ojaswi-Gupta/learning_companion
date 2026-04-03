from supabase import create_client
import vecs
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker

from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_URL

# Supabase REST client (for Storage and Postgres tables)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Vecs client for pgvector collections.
# vecs creates its own QueuePool engine internally. We immediately replace
# it with a NullPool engine so every DB operation gets a fresh TCP socket.
# This prevents the #1 cause of "connection timed out" errors on Render:
# stale pooled connections that silently died due to NAT/firewall timeouts.
vecs_client = vecs.create_client(SUPABASE_DB_URL)

# Dispose the default QueuePool engine and replace with NullPool
vecs_client.engine.dispose()
vecs_client.engine = create_engine(
    SUPABASE_DB_URL,
    poolclass=NullPool,
    connect_args={"connect_timeout": 10}
)
vecs_client.Session = sessionmaker(vecs_client.engine)
