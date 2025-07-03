import os
import sqlite3
from modules.db_validator import is_valid_sqlite, get_sha256
from modules.schema_parser import get_tables_and_columns
from modules.live_reader import read_table_records
from modules.freelist_parser import extract_freelist_pages
from modules.Btree_parser import recover_deleted_rows


def main():
    db_path = input("Enter path to SQLite DB file: ").strip()
    
    if not os.path.exists(db_path):
        print("[❌] File does not exist.")
        return

    if not is_valid_sqlite(db_path):
        print("[❌] Not a valid SQLite database.")
        return
    
    sha256 = get_sha256(db_path)
    print("[✅] Valid SQLite DB.")
    print(f"[🔐] SHA256: {sha256}")
    
    schema = get_tables_and_columns(db_path)
    if schema:
        print("[📋] Tables and Columns Found:")
        for table, columns in schema.items():
            print(f"  - {table}: {columns}")
    else:
        print("[⚠️] No tables found or failed to parse schema.")
        return

    table_names = list(schema.keys())

    print("\nAvailable Tables:")
    for idx, tname in enumerate(table_names):
        print(f"{idx + 1}. {tname}")

    try:
        choice = int(input("Select a table number to view records: "))
        selected_table = table_names[choice - 1]
    except (IndexError, ValueError):
        print("[❌] Invalid choice.")
        return

    records = read_table_records(db_path, selected_table, limit=50)
    if records:
        print(f"\n📄 Records from '{selected_table}':")
        for row in records:
            print(row)
    else:
        print("[⚠️] No records found or failed to fetch.")

    print("\n🧟 Scanning for Deleted Records...")
    freelist_results = extract_freelist_pages(db_path)
    if freelist_results:
        for result in freelist_results:
            print(f"  • Trunk Page: {result['page']} | Leaves: {result['leaf_count']}")
            print(f"    Preview: {result['ascii_preview']}")
    else:
        print("[⚠️] No deleted record pages found.")

    print("\n🔍 Attempting Structured Deleted Row Recovery...")
    deleted_rows = recover_deleted_rows(db_path, selected_table)
    if deleted_rows:
        print(f"[✅] {len(deleted_rows)} deleted rows recovered:")
        for row in deleted_rows:
            print(row)
    else:
        print("[⚠️] No recoverable deleted rows found.")

if __name__ == "__main__":
    main()
