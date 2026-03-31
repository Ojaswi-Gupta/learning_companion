from supabase import create_client
import vecs

from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_DB_URL

# Supabase REST client (for Storage and Postgres tables)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Vecs client (for pgvector collections)
vecs_client = vecs.create_client(SUPABASE_DB_URL)
