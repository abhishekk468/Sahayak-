"""
Load Sahayak CSV exports into PostgreSQL.
Install: pip install "psycopg[binary]"
1) Create an empty database.
2) Run: psql -d sahayak -f sahayak_postgresql_schema.sql
3) Set DATABASE_URL, then run: python load_sahayak_postgres.py ./csv
"""
import csv, os, sys
import psycopg

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:YOUR_PASSWORD@localhost:5432/sahayak")
CSV_DIR = sys.argv[1] if len(sys.argv) > 1 else "./csv"

TABLE_CONFIG = {
    "schemes.csv": ("schemes", ["scheme_id","scheme_name","coverage","segment","objective","benefit_summary","candidate_profile","application_channel","official_source_url","source_detail_url","eligibility_mode","source_confidence","data_notes"]),
    "eligibility_rules.csv": ("eligibility_rules", ["rule_id","scheme_id","rule_group","field_name","operator","value","action","condition_explanation","official_source_url","source_section","automation_status"]),
    "scheme_documents.csv": ("scheme_documents", ["scheme_id","documents_or_evidence_to_prepare","official_source_url","notes"]),
    "official_sources.csv": ("official_sources", ["source_id","source_title","publisher","data_used","url","usage_note"]),
}
def main():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            for filename, (table, columns) in TABLE_CONFIG.items():
                path = os.path.join(CSV_DIR, filename)
                if not os.path.exists(path):
                    raise FileNotFoundError(path)
                with open(path, newline="", encoding="utf-8-sig") as f:
                    reader = csv.DictReader(f)
                    placeholders = ",".join(["%s"] * len(columns))
                    col_sql = ",".join(columns)
                    insert_sql = f"INSERT INTO {table} ({col_sql}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                    for row in reader:
                        cur.execute(insert_sql, [row.get(c) or None for c in columns])
        conn.commit()
    print("Sahayak scheme data loaded.")
if __name__ == "__main__":
    main()
