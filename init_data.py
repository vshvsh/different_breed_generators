import pandas as pd
import requests
import sqlite3
import streamlit as st


@st.cache_data  # 👈 Add the caching decorator
def connect_to_db():
    return make_db_uri()


# export function to create a mysql in memory db and fill it with data
def make_db_uri():
    # URL of the file
    url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vTLLVgx5ygrIfZ_nT0RsXV69I1j1nkfUMvztdkSXURPt2U9hMa9WCf2tgkKQoVDnsy2ZQt2w-m4rx7J/pub?output=xlsx'

    # Send a GET request to the URL
    response = requests.get(url)

    # Save the content of the request as a file
    with open('downloaded_file.xlsx', 'wb') as f:
        f.write(response.content)

    # Load the Excel file again
    excel_file = 'downloaded_file.xlsx'
    sheets = pd.read_excel(excel_file, sheet_name=None)

    db_uri = 'file:adbdb:?mode=memory&cache=shared'
    # Create an in-memory SQLite database and load all sheets as tables
    conn = sqlite3.connect(db_uri)

    for sheet_name, df in sheets.items():
        df.to_sql(sheet_name, conn, index=False, if_exists='replace')

    # Verify the tables loaded
    tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';",
                         conn)
    return db_uri
