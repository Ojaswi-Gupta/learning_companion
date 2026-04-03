from supabase import create_client
import vecs

from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_URL

# Supabase REST client (for Storage and Postgres tables)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Vecs client (for pgvector collections)
# We forcefully swap to port 6543 to use the Transaction Pooler, preventing all ghost connection queue locks natively.
TRANSACTION_URL = SUPABASE_DB_URL.replace(":5432", ":6543") if SUPABASE_DB_URL else ""
vecs_client = vecs.create_client(TRANSACTION_URL)

# Fix for Render idle connection dropouts
vecs_client.engine.pool._recycle = 10
vecs_client.engine.pool._pre_ping = True
