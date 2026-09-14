import os
import httpx
import asyncio
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

async def get_isda_access_token(username: str, password: str) -> str:
    url = "https://api.isda-africa.com/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "password",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "string",
        "client_secret": "string",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(url, headers=headers, data=data)
        response.raise_for_status()
        return response.json()["access_token"]

async def fetch_isda_soil_property(lat: float, lon: float, depth: str = "0-20") -> dict:
    access_token = await get_isda_access_token(
        os.getenv("ISDA_USERNAME"), os.getenv("ISDA_PASSWORD")
    )
    url = "https://api.isda-africa.com/isdasoil/v2/soilproperty"
    params = {"lat": lat, "lon": lon, "depth": depth}
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        data["coordinates"] = {"lat": lat, "lon": lon}
        properties = data["property"]
        llm_ready_data = {}
        common_depth = None

        for prop_name, entries in properties.items():
            if not entries:
                continue

            entry = entries[0]  # Each property contains a list with one dict

            # Extract common depth (only once)
            if common_depth is None and "depth" in entry:
                common_depth = entry["depth"]

            value_info = entry["value"]
            value = value_info.get("value")
            typee = value_info.get("type")
            unit = value_info.get("unit")

            # Build the property summary
            result = {
                "unit": unit,
                "type": typee,
                "predicted_value": value
            }

            # Add 90% confidence interval
            uncertainty = entry.get("uncertainty")
            if uncertainty:
                ci_90 = next((ci for ci in uncertainty if ci["confidence_interval"] == "90%"), None)
                if ci_90:
                    result["interval_for_value_90pct"] = {
                        "lower_bound": ci_90["lower_bound"],
                        "upper_bound": ci_90["upper_bound"]
                    }

            llm_ready_data[prop_name] = result

        # Final output with coordinates, common depth, and cleaned properties
        final_output = {
            "coordinates": data["coordinates"],
            "depth": common_depth,
            "properties": llm_ready_data
        }

        return final_output

if __name__ == "__main__":
    lat=float(input("Enter latitude: "))
    lon=float(input("Enter longitude: "))
    result = asyncio.run(fetch_isda_soil_property(lat, lon))
    with open('isda_soil_property.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
