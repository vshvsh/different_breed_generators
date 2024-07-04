import streamlit as st
import pandas as pd
import sqlite3
from collections import Counter

from init_data import make_db_uri
from queries import prepare_data

st.write("navigate generators in the left sidebar")
create_page = st.Page("pages_create_vehicle.py", title="Create vehicle")
refit_page = st.Page("pages_refit_squad.py", title="Refit squad")
refit_warhost_page = st.Page("pages_refit_warhosts.py", title="Refit warhosts")
ng = st.navigation([create_page, refit_page, refit_warhost_page])
ng.run()
