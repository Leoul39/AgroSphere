from httpx import Client, Timeout
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os


load_dotenv()

user=os.getenv('db_user')
password=os.getenv('db_password')

def extract_transform_soil_data(lat, lon):
    def convert_nitrogen_to_kg_ha(n_cg_per_kg, bd_cg_per_cm3, depth_cm=5):
        n_g_per_kg = n_cg_per_kg / 100
        bd_g_per_cm3 = bd_cg_per_cm3 / 100
        return n_g_per_kg * bd_g_per_cm3 * depth_cm * 0.1
    '''
    Extracts and transforms soil property data for a given 
    latitude and longitude from the OpenEPI API.
    
    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
    
    Returns:
        pd.DataFrame: A DataFrame containing soil property values 
        (mean, Q0.5, Q0.05) for each property and depth.
    '''
    with Client(timeout=60.0) as client:
        # Fetch and extract properties at two depths
        response = client.get(
            url="https://api.openepi.io/soil/property",
            params={
                "lat": lat,
                "lon": lon,
                "depths": "0-5cm", 
                "properties": ["bdod", "phh2o", "soc", "clay", "sand", "cec","nitrogen","cfvo"],
                "values": "mean",
            },
        )
        data = response.json()

        
        # Prepare a list to collect rows
        records = []
        missing_data = False

        # Loop through each soil property layer
        for layer in data["properties"]["layers"]:
            code = layer["code"]
            name = layer["name"]
            mapped_units = layer["unit_measure"]["mapped_units"]
            target_units = layer["unit_measure"]["target_units"]

            for depth in layer["depths"]:
                label = depth["label"]
                values = depth["values"]
                mean_value = values.get("mean")
                # Adjust pH value if applicable
                if code == "phh2o" and mean_value is not None:
                    mean_value = mean_value / 10
                # Convert nitrogen from g/kg to kg/ha if applicable
                if code == "nitrogen" and mean_value is not None:
                    # Find bulk density for the same depth
                    bd_value = None
                    for bd_layer in data["properties"]["layers"]:
                        if bd_layer["code"] == "bdod":
                            for bd_depth in bd_layer["depths"]:
                                if bd_depth["label"] == label:
                                    bd_value = bd_depth["values"].get("mean")
                    if bd_value is not None:
                        mean_value = convert_nitrogen_to_kg_ha(mean_value, bd_value, depth_cm=5)
                if mean_value is None:
                    missing_data = True
                row = {
                    "latitude": lat,
                    "longitude": lon,
                    "code": code,
                    "name": name,
                    "mapped_units": mapped_units,
                    "target_units": target_units,
                    "depth_label": label,
                    "mean": mean_value,
                }
                records.append(row)

        if missing_data:
            raise ValueError("The selected coordinate does not have available soil data. Try selecting another location, preferably in a rural or agricultural area.")

        # Convert to DataFrame
        df = pd.DataFrame(records)
        df.columns = df.columns.str.replace('.', '_')
        return df

def extract_transform_soil_prob(lat,lon,top_k=5):
    '''
    Fetches the top-k most probable soil types for a given latitude and 
    longitude from the OpenEPI API.
    
    Parameters:
        lat (float): Latitude of the location.
        lon (float): Longitude of the location.
        top_k (int): Number of top probable soil types to retrieve 
        (default is 5).
    
    Returns:
        pd.DataFrame: A DataFrame containing the soil types and their 
        probabilities for the location.
    '''
    timeout = Timeout(20.0)
    url = "https://api.openepi.io/soil/type"
    params = {"lat": lat, "lon": lon, "top_k": top_k}
    with Client(timeout=timeout) as client:
        response = client.get(url=url, params=params)
        if response.status_code == 200:
            data = response.json()
        else:
            print(f"Failed to fetch soil data: {response.status_code}")
        # Extract most probable
        most_probable = data["properties"]["most_probable_soil_type"]

        # Flatten the probabilities
        rows = []
        for item in data["properties"]["probabilities"]:
            rows.append({
                "latitude": lat,
                "longitude": lon,
                "soil_type": item["soil_type"],
                "probability_percent": str(item["probability"]) + "%"
            })

        # Create DataFrame
        df = pd.DataFrame(rows)

        return df
    
def load_to_postgres(df, table_name, db_name="soil_info_db", user=user, password=password, host="localhost", port=5432):
    '''
    Loads a DataFrame into a PostgreSQL database table.
    '''
    try:
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}")
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"Data loaded into '{table_name}' successfully.")
    except Exception as e:
        print(f"Error loading to PostgreSQL: {e}")




    