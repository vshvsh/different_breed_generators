import streamlit as st
import pandas as pd


@st.cache_data  # 👈 Add the caching decorator
def prepare_data(_conn):
  query = """
  SELECT *
  FROM "VehicleChassis"
  """

  vehicle_chassis = pd.read_sql(query, _conn)
  vehicle_chassis_dict = vehicle_chassis.set_index('Type').to_dict(
      orient='index')

  query = """
  SELECT *
  FROM "GroundWeapons"
  """

  ground_weapons_df = pd.read_sql(query, _conn)
  ground_weapons_grouped = {
      size: group.set_index('Name').to_dict('index')
      for size, group in ground_weapons_df.groupby('Size')
  }

  query = """
  SELECT *
  FROM "VehicleSlotCosts"
  """

  vehicle_slot_costs = pd.read_sql(query, _conn)
  vehicle_slot_costs_dict = vehicle_slot_costs.set_index('Slot Type').to_dict(
      orient='index')

  query = """
  SELECT *
  FROM "VehicleSlotsConversion"
  """

  vehicle_slots_conversion = pd.read_sql(query, _conn)

  query = """
  SELECT *
  FROM "VehicleWargear"
  """
  vehicle_wargear = pd.read_sql(query, _conn)
  vehicle_wargear_dict = vehicle_wargear.set_index('Name').to_dict(
      orient='index')

  return vehicle_chassis_dict, ground_weapons_grouped, vehicle_slot_costs_dict, vehicle_slots_conversion, vehicle_wargear_dict
