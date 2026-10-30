CREATE TABLE IF NOT EXISTS schemes (
  scheme_id TEXT PRIMARY KEY,
  scheme_name TEXT NOT NULL,
  coverage TEXT NOT NULL,
  segment TEXT NOT NULL,
  objective TEXT,
  benefit_summary TEXT,
  candidate_profile TEXT,
  application_channel TEXT,
  official_source_url TEXT NOT NULL,
  source_detail_url TEXT,
  eligibility_mode TEXT NOT NULL,
  source_confidence TEXT,
  data_notes TEXT,
  last_verified_on DATE DEFAULT DATE '2026-10-30'
);

CREATE TABLE IF NOT EXISTS eligibility_rules (
  rule_id TEXT PRIMARY KEY,
  scheme_id TEXT NOT NULL REFERENCES schemes(scheme_id),
  rule_group TEXT NOT NULL,
  field_name TEXT NOT NULL,
  operator TEXT NOT NULL,
  value TEXT,
  action TEXT NOT NULL CHECK (action IN ('REQUIRE','EXCLUDE','MANUAL_REVIEW')),
  condition_explanation TEXT,
  official_source_url TEXT NOT NULL,
  source_section TEXT,
  automation_status TEXT
);

CREATE TABLE IF NOT EXISTS scheme_documents (
  document_id BIGSERIAL PRIMARY KEY,
  scheme_id TEXT NOT NULL REFERENCES schemes(scheme_id),
  documents_or_evidence_to_prepare TEXT,
  official_source_url TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS official_sources (
  source_id TEXT PRIMARY KEY,
  source_title TEXT NOT NULL,
  publisher TEXT,
  data_used TEXT,
  url TEXT NOT NULL,
  usage_note TEXT
);

CREATE TABLE IF NOT EXISTS citizen_profiles (
  profile_id TEXT PRIMARY KEY,
  consent_status TEXT NOT NULL DEFAULT 'NOT_COLLECTED',
  profile_data JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_interactions (
  interaction_id BIGSERIAL PRIMARY KEY,
  profile_id TEXT REFERENCES citizen_profiles(profile_id),
  channel TEXT,
  language_code TEXT,
  intent TEXT,
  transcript_text TEXT,
  audio_deleted BOOLEAN DEFAULT FALSE,
  asr_confidence NUMERIC(5,4),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS rag_documents (
  rag_document_id TEXT PRIMARY KEY,
  scheme_id TEXT REFERENCES schemes(scheme_id),
  document_title TEXT NOT NULL,
  official_url TEXT NOT NULL,
  publisher TEXT,
  version_or_published_date TEXT,
  page_or_section TEXT,
  fetched_on DATE,
  ingestion_status TEXT
);

CREATE TABLE IF NOT EXISTS rag_chunks (
  chunk_id TEXT PRIMARY KEY,
  rag_document_id TEXT NOT NULL REFERENCES rag_documents(rag_document_id),
  scheme_id TEXT REFERENCES schemes(scheme_id),
  chunk_text TEXT NOT NULL,
  page_or_section TEXT,
  embedding_ref TEXT,
  source_url TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS eligibility_results (
  result_id BIGSERIAL PRIMARY KEY,
  profile_id TEXT REFERENCES citizen_profiles(profile_id),
  scheme_id TEXT NOT NULL REFERENCES schemes(scheme_id),
  match_status TEXT NOT NULL,
  reasons JSONB NOT NULL DEFAULT '[]'::jsonb,
  evaluated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS application_tracker (
  application_id BIGSERIAL PRIMARY KEY,
  profile_id TEXT REFERENCES citizen_profiles(profile_id),
  scheme_id TEXT NOT NULL REFERENCES schemes(scheme_id),
  application_status TEXT,
  next_action TEXT,
  reminder_at TIMESTAMPTZ,
  official_application_url TEXT,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS district_insights_daily (
  insight_date DATE NOT NULL,
  district TEXT NOT NULL,
  language_code TEXT,
  intent TEXT,
  scheme_id TEXT REFERENCES schemes(scheme_id),
  interaction_count INTEGER NOT NULL DEFAULT 0,
  unresolved_count INTEGER NOT NULL DEFAULT 0,
  avg_asr_confidence NUMERIC(5,4),
  PRIMARY KEY (insight_date,district,language_code,intent,scheme_id)
);
