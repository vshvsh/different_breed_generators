import streamlit as st
import pandas as pd
import sqlite3


@st.cache_data  # 👈 Add the caching decorator
def prepare_data(connect_string):
    _conn = sqlite3.connect(connect_string)
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
    vehicle_slot_costs_dict = vehicle_slot_costs.set_index(
        'Slot Type').to_dict(orient='index')

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


@st.cache_data  # 👈 Add the caching decorator
def prepare_squads_refit_data(connect_string):
    _conn = sqlite3.connect(connect_string)
    query = 'SELECT * FROM Squads'
    df = pd.read_sql(query, _conn)
    squad_types = df.set_index('Squad Type').to_dict(orient='index')

    query = f'''
    SELECT 
        s."Squad Type",
        sv."Vehicle Type",
        SUM(sv."Quantity") as "Total Vehicles"
    FROM 
        squads s
    JOIN 
        SquadsVehicles sv
    ON 
        s."Squad Type" = sv."Squad Type"
    GROUP BY 
        s."Squad Type", sv."Vehicle Type"
    ORDER BY 
        s."Squad Type";
    '''

    vehicles_by_squad = pd.read_sql(query, _conn)

    for squad_type in squad_types.keys():
        # Filter the rows for the current squad type

        # Select troops from troops table
        query = f"SELECT `Squad Type`, `Troop Type`, `Count`, `Armor`, `Weapons`, `Equipment` FROM troops WHERE `Squad Type` = '{squad_type}'"
        troops_list = pd.read_sql(query, _conn)

        # Convert DataFrame to list of dicts
        troops_list_dicts = troops_list.drop(columns=['Squad Type']).to_dict(
            orient='records')

        # Add troops list to squads list
        squad_types[squad_type]['Troops'] = troops_list_dicts

        squad_types[squad_type]['Vehicles'] = vehicles_by_squad[
            vehicles_by_squad['Squad Type'] == squad_type].set_index(
                'Vehicle Type')['Total Vehicles'].to_dict()

    query = """
  SELECT d.`Squad Type`, d.`Detachment Type`, Sum(d.`Quantity`) as `Count`
  FROM DetachmentsSquads d
  GROUP BY d.`Detachment Type`, d.`Squad Type`
  ORDER BY d.`Squad Type`;
  """
    detachments_with_squad_counts = pd.read_sql(query, _conn)

    detachments_with_squads_dicts = detachments_with_squad_counts.to_dict(
        orient='records')
    detachments_dict = {}
    for item in detachments_with_squads_dicts:
        squad_type = item['Squad Type']
        if squad_type not in detachments_dict:
            detachments_dict[squad_type] = {}
        detachments_dict[squad_type][item['Detachment Type']] = item['Count']

    query = '''
    SELECT 
       *
    FROM 
        WarhostDetachments
    Order by "Warhost Name";
    '''
    warhost_detachments = pd.read_sql(query, _conn)

    # Replace repeated Warhost Name with blank space
    warhost_detachments["Warhost Name"] = warhost_detachments[
        "Warhost Name"].mask(warhost_detachments["Warhost Name"].duplicated(),
                             '')

    query = '''
    SELECT 
        "Detachment Type",
        sum("Count") as "Total"
    FROM 
        WarhostDetachments
    group BY 
        "Detachment Type";
    '''
    detachments_total = pd.read_sql(query, _conn)

    query = '''
    SELECT 
        ds."Squad Type",
        wd."Warhost Name",
        SUM(ds."Quantity"*wd."Count") as "Total",
        SUM(ds."Quantity"*wd."Count"*s."Total People")  as "Total People",
        ifnull(SUM(ds."Quantity"*wd."Count"*sv."Quantity"),0)  as "Total Vehicles"
    FROM 
        DetachmentsSquads ds
    JOIN 
        WarhostDetachments wd
    ON 
        ds."Detachment Type" = wd."Detachment Type"
    JOIN 
        Squads s
    ON 
        ds."Squad Type" = s."Squad Type"
    LEFT JOIN 
        SquadsVehicles sv
    ON 
        ds."Squad Type" = sv."Squad Type"
    GROUP BY ds."Squad Type", wd."Warhost Name"
    ORDER BY 
        ds."Squad Type";
    '''
    squads_totals = pd.read_sql(query, _conn)

    # Compute the totals for each squad type
    squad_totals_summary = squads_totals.groupby(
        'Squad Type').sum().reset_index()
    squad_totals_summary['Warhost Name'] = 'Total'

    # Insert the summary rows after the corresponding squad type
    for idx, row in squad_totals_summary.iterrows():
        squad_type = row['Squad Type']
        insert_idx = squads_totals[squads_totals['Squad Type'] ==
                                   squad_type].index[-1] + 1
        squads_totals = pd.concat([
            squads_totals.iloc[:insert_idx],
            row.to_frame().T, squads_totals.iloc[insert_idx:]
        ]).reset_index(drop=True)

    # Clean up repeating squad type rows
    squads_totals['Squad Type'] = squads_totals['Squad Type'].mask(
        squads_totals['Squad Type'].duplicated(), '')

    query = '''
    SELECT 
        ds."Squad Type",
        ds."Detachment Type",
        wd."Warhost Name",
        SUM(ds."Quantity"*wd."Count") as "Total"
    FROM 
        DetachmentsSquads ds
    JOIN 
        WarhostDetachments wd
    ON 
        ds."Detachment Type" = wd."Detachment Type"
    JOIN 
        Squads s
    ON 
        ds."Squad Type" = s."Squad Type"
    GROUP BY ds."Squad Type",ds."Detachment Type", wd."Warhost Name"
    ORDER BY 
        ds."Squad Type";
    '''
    squads_dataset = pd.read_sql(query, _conn)

    query = 'SELECT * FROM InfantryArmor'
    infantry_armor = pd.read_sql(query, _conn)
    infantry_armor = infantry_armor.set_index('Name').to_dict(orient='index')

    query = 'SELECT * FROM InfantryWargear'
    infantry_wargear = pd.read_sql(query, _conn)
    infantry_wargear = infantry_wargear.set_index('Name').to_dict(
        orient='index')

    query = """
    SELECT *
    FROM "GroundWeapons"
    WHERE "Size" NOT IN ('Superheavy Weapon', 'Vehicle Weapon')
    """

    infantry_weapons_df = pd.read_sql(query, _conn)
    infantry_weapons = infantry_weapons_df.set_index('Name').to_dict('index')

    return squad_types, detachments_dict, warhost_detachments, detachments_total, squads_totals, squads_dataset, infantry_armor, infantry_wargear, infantry_weapons
