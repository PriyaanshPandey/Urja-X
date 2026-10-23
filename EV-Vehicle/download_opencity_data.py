import os
import requests

OPENCITY_API = "https://data.opencity.in/api/3/action/package_search"
DOWNLOAD_DIR = "./opencity_ev_data"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Key queries matching EV infrastructure, consumption, and city registrations
SEARCH_QUERIES = [
    "EV charging",
    "EV consumption",
    "BESCOM EV",
    "Hyderabad EV",
    "vehicle registration"
]

def sanitize_filename(name):
    return "".join(c if c.isalnum() or c in (" ", "_", "-") else "_" for c in name).strip()

def fetch_and_download():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) EV-Infra-Researcher"
    }
    
    seen_resources = set()

    for query in SEARCH_QUERIES:
        print(f"\nSearching OpenCity for: '{query}'...")
        params = {
            "q": query,
            "rows": 20
        }
        
        try:
            res = requests.get(OPENCITY_API, params=params, headers=headers, timeout=20)
            if res.status_code != 200:
                print(f"  [-] Failed with HTTP {res.status_code}")
                continue
            
            data = res.json()
            packages = data.get("result", {}).get("results", [])
            print(f"  [+] Found {len(packages)} packages.")

            for pkg in packages:
                pkg_title = pkg.get("title", "dataset")
                resources = pkg.get("resources", [])

                for r in resources:
                    r_id = r.get("id")
                    r_format = r.get("format", "").upper()
                    r_url = r.get("url")
                    r_name = r.get("name") or pkg_title

                    # Prioritize structured tabular & spatial files
                    if r_id not in seen_resources and r_format in ["CSV", "XLSX", "XLS", "GEOJSON", "JSON"]:
                        seen_resources.add(r_id)
                        
                        ext = r_format.lower()
                        clean_name = sanitize_filename(f"{pkg_title}_{r_name}")[:100]
                        file_path = os.path.join(DOWNLOAD_DIR, f"{clean_name}.{ext}")
                        
                        print(f"    -> Downloading: {clean_name}.{ext}")
                        try:
                            file_req = requests.get(r_url, headers=headers, stream=True, timeout=30)
                            if file_req.status_code == 200:
                                with open(file_path, "wb") as f:
                                    for chunk in file_req.iter_content(chunk_size=8192):
                                        f.write(chunk)
                                print(f"       [Saved: {file_path}]")
                            else:
                                print(f"       [Failed: HTTP {file_req.status_code}]")
                        except Exception as e:
                            print(f"       [Error downloading {r_url}: {e}]")

        except Exception as e:
            print(f"  [-] Error querying OpenCity: {e}")

    print("\nDownload process completed! Check ./opencity_ev_data")

if __name__ == "__main__":
    fetch_and_download()