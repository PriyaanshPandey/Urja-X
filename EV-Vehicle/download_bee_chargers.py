# import os
# import time
# import requests
# import pandas as pd

# SAVE_DIR = "./charging_infra_raw"
# os.makedirs(SAVE_DIR, exist_ok=True)

# # Open Charge Map Public Endpoint
# # Optional: Register a free API key at openchargemap.org/site/develop/api to raise rate limits
# OCM_API = "https://api.openchargemap.io/v3/poi"
# # Public default key parameter or pass your X-API-Key in headers
# API_KEY = "64c8c278-f682-4161-825f-c56a81bfaeb5"  # Community dev key

# def fetch_india_chargers(max_results=5000):
#     """
#     Pulls geolocated charging points for India (ISO: IN).
#     Extracts connector types, kW capacities, operator metadata, and coordinates.
#     """
#     print("Connecting to public charger registry for India...")
#     params = {
#         "output": "json",
#         "countrycode": "IN",
#         "maxresults": max_results,
#         "compact": False,
#         "verbose": True,
#         "key": API_KEY
#     }
#     headers = {
#         "User-Agent": "EV-Infra-Research/1.0"
#     }

#     try:
#         response = requests.get(OCM_API, params=params, headers=headers, timeout=45)
#         if response.status_code != 200:
#             print(f"Failed with status code: {response.status_code}")
#             return None
        
#         data = response.json()
#         print(f"[+] Retrieved {len(data)} charging station records.")

#         parsed_records = []
#         for item in data:
#             station_id = item.get("ID")
#             title = item.get("AddressInfo", {}).get("Title")
#             address = item.get("AddressInfo", {}).get("AddressLine1")
#             town = item.get("AddressInfo", {}).get("Town")
#             state = item.get("AddressInfo", {}).get("StateOrProvince")
#             postcode = item.get("AddressInfo", {}).get("Postcode")
#             lat = item.get("AddressInfo", {}).get("Latitude")
#             lon = item.get("AddressInfo", {}).get("Longitude")
            
#             operator_info = item.get("OperatorInfo", {})
#             operator = operator_info.get("Title", "Unknown / Private") if operator_info else "Unknown"

#             # Parse connectors / power levels
#             connections = item.get("Connections", [])
#             total_points = len(connections) if connections else 1
#             max_kw = 0.0
#             connector_types = []

#             for conn in connections:
#                 power_kw = conn.get("PowerKW")
#                 if power_kw:
#                     try:
#                         max_kw = max(max_kw, float(power_kw))
#                     except ValueError:
#                         pass
#                 conn_type = conn.get("ConnectionType", {}).get("Title")
#                 if conn_type and conn_type not in connector_types:
#                     connector_types.append(conn_type)

#             parsed_records.append({
#                 "Station_ID": station_id,
#                 "Station_Name": title,
#                 "Operator": operator,
#                 "Address": address,
#                 "City": town,
#                 "State": state,
#                 "PostalCode": postcode,
#                 "Latitude": lat,
#                 "Longitude": lon,
#                 "Total_Plugs": total_points,
#                 "Max_Power_kW": max_kw if max_kw > 0 else 15.0,  # Default to standard Bharat DC slow baseline
#                 "Connector_Types": ", ".join(connector_types) if connector_types else "Standard Type-2 / Bharat DC"
#             })

#         df = pd.DataFrame(parsed_records)
        
#         # Save as CSV and Spatial-ready Parquet
#         csv_file = os.path.join(SAVE_DIR, "national_chargers_registry.csv")
#         parquet_file = os.path.join(SAVE_DIR, "national_chargers_registry.parquet")
        
#         df.to_csv(csv_file, index=False)
#         df.to_parquet(parquet_file, index=False)
#         print(f"[OK] Saved geolocated stations to:\n  - {csv_file}\n  - {parquet_file}")
#         return df

#     except Exception as e:
#         print(f"Error fetching charging infrastructure data: {e}")
#         return None

# if __name__ == "__main__":
#     fetch_india_chargers()

import os
import requests
import pandas as pd

SAVE_DIR = "./charging_infra_raw"
os.makedirs(SAVE_DIR, exist_ok=True)

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

def fetch_india_chargers_osm():
    print("Querying OpenStreetMap Overpass API for all EV chargers in India...")
    
    # Overpass QL query: fetches all nodes and ways with amenity=charging_station in India
    query = """
    [out:json][timeout:90];
    area["ISO3166-1"="IN"][admin_level=2]->.india;
    (
      node["amenity"="charging_station"](area.india);
      way["amenity"="charging_station"](area.india);
    );
    out center tags;
    """

    headers = {
        "User-Agent": "EV-Infra-Map-India-Academic/1.0"
    }

    try:
        response = requests.post(OVERPASS_URL, data={"data": query}, headers=headers, timeout=120)
        if response.status_code != 200:
            print(f"[-] Overpass API error: HTTP {response.status_code}")
            return None

        elements = response.json().get("elements", [])
        print(f"[+] Retrieved {len(elements)} charging stations from OpenStreetMap.")

        records = []
        for el in elements:
            tags = el.get("tags", {})
            
            # Extract coordinates (handles both point nodes and polygon centers)
            lat = el.get("lat") or el.get("center", {}).get("lat")
            lon = el.get("lon") or el.get("center", {}).get("lon")
            
            if not lat or not lon:
                continue

            records.append({
                "Station_ID": f"OSM_{el.get('type')}_{el.get('id')}",
                "Station_Name": tags.get("name", "Unnamed Charging Station"),
                "Operator": tags.get("operator", tags.get("brand", "Independent / Unspecified")),
                "Capacity_Sockets": tags.get("capacity", "1"),
                "Max_Power_kW": tags.get("socket:type2:output", tags.get("socket:chademo:output", "15.0")),
                "Access": tags.get("access", "yes"),
                "Fee": tags.get("fee", "unknown"),
                "Latitude": lat,
                "Longitude": lon,
                "City": tags.get("addr:city", ""),
                "State": tags.get("addr:state", ""),
                "Source": "OpenStreetMap"
            })

        df = pd.DataFrame(records)
        csv_path = os.path.join(SAVE_DIR, "national_chargers_registry.csv")
        df.to_csv(csv_path, index=False)
        print(f"[OK] Successfully saved {len(df)} stations to: {csv_path}")
        return df

    except Exception as e:
        print(f"[-] Extraction failed: {e}")
        return None

if __name__ == "__main__":
    fetch_india_chargers_osm()