import streamlit as st
import pandas as pd
import sqlite3
from collections import Counter

from init_data import connect_to_db
from queries import prepare_data

db_uri = connect_to_db()
conn = sqlite3.connect(db_uri)

vehicle_chassis_dict, ground_weapons_grouped, vehicle_slot_costs_dict, vehicle_slots_conversion, vehicle_wargear_dict = prepare_data(
    conn)

st.title("Create vehicle")

vehicle_design = {}
name = st.text_input("Enter vehicle name")
if not name:
  name = "placeholder"

vehicle_vote = "[x] Plan " + name + "\n"

chassis = st.selectbox("Select chassis", vehicle_chassis_dict.keys())
if (chassis):
  vehicle_design = vehicle_chassis_dict[chassis]
  vehicle_vote += "-[x] Chassis: " + chassis + "\n"
  vehicle_design['Chassis'] = chassis
  vehicle_design['SS spent'] = 0
  vehicle_design['SS refunded'] = 0
  vehicle_design['Gear EP costs'] = 0
  vehicle_design['Starcrystals'] = 0
  vehicle_design['Psy-Scopes'] = 0
  vehicle_design['Weapons'] = {}

#slot add/refund
for stype in vehicle_slot_costs_dict:
  inp = st.number_input("Add/refund " + stype + " slots",
                        value=0,
                        min_value=-vehicle_design[stype + ' Slots'],
                        max_value=100)
  if inp > 0:
    vehicle_design[stype + ' Slots'] += inp
    ss_cost = inp * vehicle_slot_costs_dict[stype]['System Slots Required']
    vehicle_design['SS spent'] += ss_cost
    vehicle_vote += "-[x] Add " + str(inp) + " " + stype + " slots, " + str(
        ss_cost) + " SS\n"
  elif inp < 0:
    vehicle_design[stype + ' Slots'] += inp
    ss_cost = inp * vehicle_slot_costs_dict[stype]['System Slots Refunded']
    vehicle_design['SS refunded'] -= round(ss_cost)
    vehicle_vote += "-[x] Refund " + str(
        inp) + " " + stype + " slots for " + str(abs(ss_cost)) + " SS\n"

#slot conversion
for stype in reversed(vehicle_slot_costs_dict.keys()):
  if vehicle_design[stype + ' Slots'] > 0 and stype != 'Ranged Weapon':
    inp = st.number_input("Downgrade " + stype + " slots",
                          value=0,
                          min_value=0,
                          max_value=vehicle_design[stype + ' Slots'])
    if inp > 0:
      type_order = {
          'Superheavy Weapon': ('Vehicle Weapon', 3),
          'Vehicle Weapon': ('Heavy Weapon', 2),
          'Heavy Weapon': ('Ranged Weapon', 2),
      }
      vehicle_design[stype + ' Slots'] -= inp
      vehicle_design[type_order[stype][0] +
                     ' Slots'] += inp * type_order[stype][1]
      vehicle_vote += "-[x] Downgrade " + str(
          inp) + " " + stype + " slots to " + str(
              type_order[stype][1] *
              inp) + " " + type_order[stype][0] + " slots\n"

for stype in reversed(vehicle_slot_costs_dict.keys()):
  slots = vehicle_design[stype + ' Slots']
  if slots > 0:
    st.write(f"{stype}s:")
    for i in range(0, slots):
      weapon = st.selectbox("Select weapon",
                            ground_weapons_grouped[stype].keys(),
                            key=str(i) + stype)
      if weapon:
        vehicle_design['Weapons'].setdefault(stype, []).append(weapon)

for stype in vehicle_design['Weapons']:
  cnt = Counter(vehicle_design['Weapons'][stype])
  for weapon in cnt:
    weapon_stats = ground_weapons_grouped[stype][weapon]
    weapon_ep = weapon_stats['EP']
    weapon_starcrystals = weapon_stats['Starcrystals']
    weapon_psy_scopes = weapon_stats['Psy-Scopes']
    total_ep = weapon_ep * cnt[weapon]
    total_sc = weapon_starcrystals * cnt[weapon]
    total_ps = weapon_psy_scopes * cnt[weapon]
    vehicle_design['Gear EP costs'] += total_ep
    vehicle_design['Starcrystals'] += total_sc
    vehicle_design['Psy-Scopes'] += total_ps
    vehicle_vote += f"-[x] Add {cnt[weapon]} {stype} {weapon} ({total_ep} EP, {total_sc} Starcrystals, {total_ps} Psy-Scopes)\n"

wargear_cnt = st.number_input("Add wargear", value=0, min_value=0, max_value=5)

st.write("Wargear:")

for i in range(0, wargear_cnt):
  wg = st.selectbox("Select wargear",
                    vehicle_wargear_dict.keys(),
                    key=str(i) + "wargear")
  amount = st.number_input("Number",
                           value=1,
                           min_value=1,
                           max_value=60,
                           key=str(i) + "wargearcnt")
  if wg:
    wg_stats = vehicle_wargear_dict[wg]
    wg_ep = wg_stats['EP']
    wg_ss = wg_stats['Slot Cost']

    total_ep = wg_ep * amount
    total_ss = wg_ss * amount
    vehicle_design['Gear EP costs'] += total_ep
    vehicle_design['SS spent'] += total_ss
    vehicle_vote += f"-[x] Add {amount} {wg} ({total_ep} EP, {total_ss} SS"
    if wg == 'Infantry Capacity (Open Top)':
      vehicle_vote += f", {int(amount*2 + amount/5)} open capacity"
    vehicle_vote += ")\n"
    if wg == 'Vehicle Holo-Field' and amount > 1:
      st.write("Warning! You can only have one Vehicle Holo-Field")
    grav_allowed = 2
    if vehicle_design['Chassis'] == 'Heavy Grav-Vehicle':
      grav_allowed = 3
    if wg == 'Vehicle Grav-Shield' and amount > grav_allowed:
      st.write(
          f"Warning! You can only have {grav_allowed} Vehicle Grav-Shield on this chassis"
      )

vehicle_vote += f"-[x] Total gear costs: {vehicle_design['Gear EP costs']} EP, {vehicle_design['Starcrystals']} Starcrystals, {vehicle_design['Psy-Scopes']} Psy-Scopes\n"
if vehicle_design['Base EP'] > 0:
  vehicle_vote += f"-[x] Total EP cost should be around {vehicle_design['Gear EP costs'] + vehicle_design['Base EP']} EP\n"

ss_left = vehicle_design['System Slots'] + vehicle_design[
    'SS refunded'] - vehicle_design['SS spent']
if ss_left < 0:
  st.write(
      f'Warning! {vehicle_design["SS spent"]} system slot spent out of {vehicle_design["System Slots"]} base + {vehicle_design["SS refunded"]} refunded'
  )

vehicle_vote += f'-[x] SS: {vehicle_design["SS spent"]} spent out of {vehicle_design["System Slots"]} base + {vehicle_design["SS refunded"]} refunded'

st.code(vehicle_vote)
