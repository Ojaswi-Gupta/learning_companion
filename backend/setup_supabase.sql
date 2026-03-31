-- Run this in your Supabase SQL Editor (supabase.com → SQL Editor → New Query)
-- These commands set up everything the AI Learning Companion needs.

-- 1. Enable the pgvector extension (for vector similarity search)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the documents metadata table
CREATE TABLE IF NOT EXISTS documents (
    doc_id   TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    topics   TEXT
);

-- 2b. RLS policies for the documents table (allow all via anon key)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public insert on documents" ON documents
  FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public select on documents" ON documents
  FOR SELECT USING (true);

CREATE POLICY "Allow public update on documents" ON documents
  FOR UPDATE USING (true) WITH CHECK (true);

CREATE POLICY "Allow public delete on documents" ON documents
  FOR DELETE USING (true);

-- 3. Create a storage bucket for uploaded PDFs
-- (Do this in the Supabase Dashboard → Storage → New Bucket → name it "uploads")
-- Set it to PUBLIC or add an RLS policy if you want authenticated access.

-- 4. Storage RLS policies (required for uploads/deletes even on public buckets)
CREATE POLICY "Allow public uploads" ON storage.objects
  FOR INSERT WITH CHECK (bucket_id = 'uploads');

CREATE POLICY "Allow public reads" ON storage.objects
  FOR SELECT USING (bucket_id = 'uploads');

CREATE POLICY "Allow public deletes" ON storage.objects
  FOR DELETE USING (bucket_id = 'uploads');
