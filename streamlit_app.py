import streamlit as st
import os
import tempfile
import sqlite3

from modules.db_validator import is_valid_sqlite, get_sha256
from modules.schema_parser import get_tables_and_columns
from modules.live_reader import read_table_records
from modules.freelist_parser import extract_freelist_pages
#from modules.Btree_parser import recover_deleted_rows
from modules.Btree_parser import recover_from_freeblocks
from modules.freeblock_parser import extract_freeblocks

st.set_page_config(page_title="SQLite Forensic Recovery", layout="wide")
st.title("🔍 SQLite Forensic Recovery Tool")

uploaded_file = st.file_uploader("Upload a SQLite database file", type=["db", "sqlite"])

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        db_path = tmp.name

    if is_valid_sqlite(db_path):
        st.success("✅ Valid SQLite DB")
        st.code(f"SHA256: {get_sha256(db_path)}", language="bash")

        schema = get_tables_and_columns(db_path)
        if not schema:
            st.warning("No tables found in this DB.")
        else:
            st.subheader("📋 Tables and Columns")
            for table, columns in schema.items():
                st.write(f"**{table}**: {columns}")

            table_names = list(schema.keys())
            selected_table = st.selectbox("Select a table to view:", table_names)

            if selected_table:
                st.subheader(f"📄 Live Records from `{selected_table}`")
                records = read_table_records(db_path, selected_table, limit=200)
                if records:
                    st.dataframe(records)
                else:
                    st.info("No live records found.")

                st.subheader("🧟 Deleted Page Preview ")
                freeblocks = extract_freeblocks(db_path, selected_table)
                if freeblocks:
                    for fb in freeblocks:
                        with st.expander(f"Page {fb['page']} @ offset {fb['freeblock_offset']} (size={fb['size']})"):
                            st.text(fb["ascii_preview"])
                else:
                    st.warning("No deleted freeblocks found.")


                st.subheader("🔬 Structured Deleted Row Recovery ")
                deleted = recover_from_freeblocks(db_path, selected_table)
                if deleted:
                    st.success(f"{len(deleted)} deleted rows recovered")
                    st.dataframe(deleted)
                else:
                    st.info("No recoverable deleted rows found.")
    else:
        st.error("❌ Not a valid SQLite database.")
