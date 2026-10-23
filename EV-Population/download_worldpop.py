"""
Automated Downloader for WorldPop India 1km Population Density GeoTIFF
Downloads unconstrained population density raster using Python HTTP stream.
"""

import sys
import urllib.request
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_TIF = DATA_DIR / "ind_pd_2020_1km.tif"

URL = "https://data.worldpop.org/GIS/Population_Density/Global_2000_2020_1km/2020/IND/ind_pd_2020_1km.tif"

def download_file():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if OUTPUT_TIF.exists() and OUTPUT_TIF.stat().st_size > 15 * 1024 * 1024:
        size_mb = OUTPUT_TIF.stat().st_size / (1024 * 1024)
        print(f"[+] WorldPop GeoTIFF already exists: {OUTPUT_TIF.name} ({size_mb:.2f} MB)")
        return True

    print(f"[*] Downloading WorldPop India 1km Population Density GeoTIFF...")
    print(f"    Source: {URL}")
    print(f"    Target: {OUTPUT_TIF}")

    req = urllib.request.Request(
        URL,
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'}
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response, open(OUTPUT_TIF, 'wb') as out_file:
            total_size = int(response.getheader('Content-Length', 0))
            downloaded = 0
            block_size = 64 * 1024 # 64 KB

            while True:
                buffer = response.read(block_size)
                if not buffer:
                    break
                out_file.write(buffer)
                downloaded += len(buffer)
                if total_size > 0:
                    percent = downloaded / total_size * 100
                    mb = downloaded / (1024 * 1024)
                    total_mb = total_size / (1024 * 1024)
                    sys.stdout.write(f"\r[+] Downloaded: {mb:.1f} MB / {total_mb:.1f} MB ({percent:.1f}%)")
                    sys.stdout.flush()

        print(f"\n[+] Successfully saved {OUTPUT_TIF.name} ({OUTPUT_TIF.stat().st_size / (1024*1024):.2f} MB)")
        return True
    except Exception as e:
        print(f"\n[!] Error downloading: {e}")
        if OUTPUT_TIF.exists():
            OUTPUT_TIF.unlink()
        return False

if __name__ == "__main__":
    success = download_file()
    sys.exit(0 if success else 1)
