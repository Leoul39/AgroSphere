import httpx
import os
from dotenv import load_dotenv
import json

# Load environment variables from .env file
load_dotenv()
opencage_api_key = os.getenv("opencage_api_key")


def get_coordinates(city_name):
    '''
    Returns the geographic center point and bounds of a major city in Ethiopia given its name.
    The function queries the OpenCage API for the city, and returns its center coordinates and bounding box.
    If the city is not found within Ethiopia's geographic bounds (3-16°N, 33-48°E), an error message is printed.
    '''
    url = f"https://api.opencagedata.com/geocode/v1/json?q={city_name}&key={opencage_api_key}"
    response = httpx.get(url)
    
    if response.status_code != 200:
        print("Error in API request:", response.status_code)
        return None
    
    data = response.json()
    if data['results']:
        coords = data['results'][0]['geometry']
        center = {"lat": coords['lat'], "lng": coords['lng']}
        # Ethiopia bounds: 3-16°N, 33-48°E
        if not (3 <= center["lat"] <= 16 and 33 <= center["lng"] <= 48):
            print("❌ There is no major city found in Ethiopia with that name.")
            return None
        bounds = data['results'][0].get('bounds')
        if bounds is not None:
            ne = bounds["northeast"]
            sw = bounds["southwest"]
            bounds = {
                "northeast": {"lat": ne["lat"], "lng": ne["lng"]},
                "southwest": {"lat": sw["lat"], "lng": sw["lng"]},
                "northwest": {"lat": ne["lat"], "lng": sw["lng"]},
                "southeast": {"lat": sw["lat"], "lng": ne["lng"]},
            }
        return {
            "center point": center,
            "bounds": bounds
        }
    else:
        print("No results found for the specified city.")
        return None


def reverse_geocode(lat, lon):
    url = f"https://api.opencagedata.com/geocode/v1/json?q={lat}+{lon}&key={opencage_api_key}&no_annotations=0"
    headers = {
        "User-Agent": "city-finder-script"
    }

    response = httpx.get(url, headers=headers)

    if response.status_code != 200:
        print("Error in API request:", response.status_code)
        return None

    data = response.json()

    data['input_coordinates'] = {'lat': lat, 'lon':lon}

    if data['results']:
        bounds_city = data['results'][0]['bounds']
        locational_components=data['results'][0]['components']
        formatted_city= data['results'][0]['formatted']
        central_location_of_formatted_city = data['results'][0]['geometry']
        distance_from_center=data['results'][0]['distance_from_q']

    return {
            "input_coordinates": data['input_coordinates'],
            "bounds_of_city": bounds_city,
            "locational_info": locational_components,
            "formatted_city": formatted_city,
            "center_of_city": central_location_of_formatted_city,
            "distance_from_city": distance_from_center
        }


if __name__ == "__main__":
    # lat = float(input("Enter latitude: "))
    # lon = float(input("Enter longitude: "))

    # result = reverse_geocode(lat, lon, opencage_api_key)

    # if result:
    #     print(f" Nearest city: {result['city']}")
    #     print(f" Region: {result['region']}")
    #     print(f" Country: {result['country']}")
    # else:
    #     print("❌ Could not find any city near the provided coordinates.")
    location = reverse_geocode(8.248, 38.080)
    print(location)
