import requests
def get_elevation(lat, lon):
    url = f"https://api.opentopodata.org/v1/srtm90m?locations={lat},{lon}"
    response = requests.get(url)
    if response.ok:
        elevation = response.json()['results'][0]['elevation']
        return elevation
    else:
        print(f"Error fetching elevation data: {response.status_code}")
        return None 

# Usage
print(get_elevation(8.75, 38.96))
