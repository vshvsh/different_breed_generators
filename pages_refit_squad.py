from numpy.core.multiarray import empty
import streamlit as st
import pandas as pd
import sqlite3

from init_data import connect_to_db
from queries import prepare_squads_refit_data

st.title("Refit squad")

db_uri = connect_to_db()

squad_types, detachments_with_squads_dicts, warhost_detachments, detachments_total, squads_total, squads_dataset, infantry_armor, infantry_wargear, infantry_weapons, vehicles = prepare_squads_refit_data(
    db_uri)

with st.expander("Army datasheets") as ex_army_datasheets:
    st.write("Total detachments:")
    st.table(detachments_total)
    st.write("Detachments by warhost:")
    warhost_detachments = pd.DataFrame(warhost_detachments)
    st.table(warhost_detachments)
    st.write("Squads by warhost and total:")
    st.table(squads_total)

#make squad refit - select squad type
squad_type = st.selectbox("Select squad type", squad_types.keys())

st.write(f'Squad type is {squad_types[squad_type]["Type"]}')

st.write('Squad troopers are:')
st.table(squad_types[squad_type]["Troops"])

if squad_types[squad_type]['Vehicles']:
    st.write('Squad vehicles are:')
    st.table(squad_types[squad_type]["Vehicles"])

with st.expander(f"{squad_type} in the army"):
    st.write('Squad is in following detachments:')
    st.table(detachments_with_squads_dicts[squad_type])

    st.write('This squad across all detachments in the army:')
    detachments_squads = squads_dataset[
        squads_dataset['Squad Type'] == squad_type].groupby(
            'Detachment Type')['Total'].sum().reset_index()
    st.table(detachments_squads)

    st.write('This squad across all warhosts:')
    warhost_squads = squads_dataset[
        squads_dataset['Squad Type'] == squad_type].groupby(
            'Warhost Name')['Total'].sum().reset_index()
    st.table(warhost_squads)

#add new armor - how many types, what types, how many
armor_num = st.number_input("Add armor types",
                            value=0,
                            min_value=0,
                            max_value=3)

squad_refit_cost = {'EP': 0, 'Starcrystals': 0, 'Psy-Scopes': 0}
squad_refit_text = "One squad refit costs:\n"

for i in range(0, armor_num):
    armor_type = st.selectbox("Select armor type",
                              infantry_armor,
                              key="armor" + str(i))
    armor_qt = st.number_input(f"Amount",
                               min_value=0,
                               max_value=12,
                               key="armorqt" + str(i))
    this_armor_costs = infantry_armor[armor_type]['EP'] * armor_qt
    squad_refit_cost['EP'] += this_armor_costs
    squad_refit_text += f'    Add {armor_qt} {armor_type} for {this_armor_costs} EP\n'

#add new armor - how many types, what types, how many
weapon_num = st.number_input("Add weapon types",
                             value=0,
                             min_value=0,
                             max_value=10)

for i in range(0, weapon_num):
    weapon_type = st.selectbox("Select weapon type",
                               infantry_weapons,
                               key="weapon" + str(i))
    weapon_qt = st.number_input(f"Amount",
                                min_value=0,
                                max_value=12,
                                key="weaponqt" + str(i))
    this_weapon_costs = infantry_weapons[weapon_type]['EP'] * weapon_qt
    this_weapon_starcrystals = infantry_weapons[weapon_type][
        'Starcrystals'] * weapon_qt
    this_weapon_psy_scopes = infantry_weapons[weapon_type][
        'Psy-Scopes'] * weapon_qt
    squad_refit_cost['EP'] += this_weapon_costs
    squad_refit_cost['Starcrystals'] += this_weapon_starcrystals
    squad_refit_cost['Psy-Scopes'] += this_weapon_psy_scopes
    squad_refit_text += f'    Add {weapon_qt} {weapon_type} for {this_weapon_costs} EP, {this_weapon_starcrystals} Starcrystals, {this_weapon_psy_scopes} Psy-Scopes\n'

#add new armor - how many types, what types, how many
wg_num = st.number_input("Add wargear types",
                         value=0,
                         min_value=0,
                         max_value=10)

for i in range(0, wg_num):
    wg_type = st.selectbox("Select armor type",
                           infantry_wargear,
                           key="wg" + str(i))
    wg_qt = st.number_input(f"Amount",
                            min_value=0,
                            max_value=12,
                            key="wgqt" + str(i))
    this_wg_costs = infantry_wargear[wg_type]['EP'] * wg_qt
    squad_refit_cost['EP'] += this_wg_costs
    squad_refit_text += f'    Add {wg_qt} {wg_type} for {this_wg_costs} EP\n'

#add new armor - how many types, what types, how many
v_num = st.number_input("Add new vehicles", value=0, min_value=0, max_value=10)

for i in range(0, v_num):
    v_type = st.selectbox("Select vehicle types", vehicles, key="v" + str(i))
    v_qt = st.number_input(f"Amount",
                           min_value=0,
                           max_value=12,
                           key="vqt" + str(i))
    this_v_costs = vehicles[v_type]['EP'] * v_qt
    this_v_starcrystals = vehicles[v_type]['Starcrystals'] * v_qt
    this_v_psy_scopes = vehicles[v_type]['Psy-Scopes'] * v_qt
    squad_refit_cost['EP'] += this_v_costs
    squad_refit_cost['Starcrystals'] += this_v_starcrystals
    squad_refit_cost['Psy-Scopes'] += this_v_psy_scopes
    squad_refit_text += f'    Add {v_qt} {v_type} for {this_v_costs} EP, {this_v_starcrystals} Starcrystals, {this_v_psy_scopes} Psy-Scopes\n'

#calculate new equipment costs by position and total
squad_refit_text += f'Total {squad_refit_cost["EP"]} EP, {squad_refit_cost["Starcrystals"]} Starcrystals, {squad_refit_cost["Psy-Scopes"]} Psy-Scopes per squad\n'
st.code(squad_refit_text)

st.write('Count number of squads per detachment and warhost')

unique_detachments = squads_dataset[squads_dataset['Squad Type'] ==
                                    squad_type]['Detachment Type'].unique()

selected_detachments = st.multiselect(
    "Select what detachments to count",
    unique_detachments,
    default=unique_detachments,
)

unique_warhosts = squads_dataset[squads_dataset['Squad Type'] ==
                                 squad_type]['Warhost Name'].unique()

selcted_warhosts = st.multiselect(
    "Select what warhosts to count",
    unique_warhosts,
    default=unique_warhosts,
)

squads_refit_total = squads_dataset[
    (squads_dataset['Squad Type'] == squad_type)
    & (squads_dataset['Detachment Type'].isin(selected_detachments)) &
    (squads_dataset['Warhost Name'].isin(selcted_warhosts))]['Total'].sum()
st.write(f'Total squads selected: {squads_refit_total}')

to_refit = st.number_input("Refit X squads", value=squads_refit_total)

#calculate new equipment costs by position and total
squad_refit_text += f'Total cost to refit across {to_refit} squads: {squad_refit_cost["EP"]*to_refit} EP, {squad_refit_cost["Starcrystals"]*to_refit} Starcrystals, {squad_refit_cost["Psy-Scopes"]*to_refit} Psy-Scopes per squad\n'
st.code(squad_refit_text)
