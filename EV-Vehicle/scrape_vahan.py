# import os
# import time
# from playwright.sync_api import sync_playwright

# VAHAN_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
# OUTPUT_DIR = "./vahan_raw_data"
# os.makedirs(OUTPUT_DIR, exist_ok=True)

# TARGET_YEARS = ["2026", "2025", "2024", "2023"]

# def run():
#     with sync_playwright() as p:
#         # Launching with headless=False lets you observe the clicks live
#         browser = p.chromium.launch(headless=False, slow_mo=300)
#         context = browser.new_context(accept_downloads=True)
#         page = context.new_page()

#         print(f"Connecting to: {VAHAN_URL}")
#         page.goto(VAHAN_URL, wait_until="domcontentloaded", timeout=60000)
#         page.wait_for_timeout(3000)

#         # 1. Set Y-Axis to 'Fuel'
#         print("Configuring Y-Axis -> 'Fuel'...")
#         # Target the dropdown located under the 'Y-Axis' heading
#         y_axis_dropdown = page.locator("div.ui-selectonemenu").filter(has_text="Vehicle Class").first
#         if not y_axis_dropdown.is_visible():
#             # Fallback locator based on position
#             y_axis_dropdown = page.locator(".ui-selectonemenu").nth(3)
#         y_axis_dropdown.click()
#         page.wait_for_timeout(800)
        
#         # Click 'Fuel' in the popup list
#         page.locator(".ui-selectonemenu-panel li").filter(has_text="Fuel").click()
#         page.wait_for_timeout(2000)

#         # 2. Iterate through Years and Download
#         for year in TARGET_YEARS:
#             print(f"\nProcessing Year: {year}")
            
#             # Select Year dropdown (currently showing '2026')
#             year_dropdown = page.locator("div.ui-selectonemenu").filter(has_text=re_compile_year()).first
#             year_dropdown.click()
#             page.wait_for_timeout(800)
            
#             page.locator(".ui-selectonemenu-panel li").filter(has_text=year).click()
#             page.wait_for_timeout(1000)

#             # Click the 'Refresh' button
#             print("Refreshing dashboard view...")
#             page.locator("button, a").filter(has_text="Refresh").click()
#             page.wait_for_load_state("networkidle")
#             page.wait_for_timeout(4000)

#             # Click the Green Excel icon to download
#             print("Capturing Excel export...")
#             try:
#                 with page.expect_download(timeout=25000) as download_info:
#                     # Target the Excel export image/icon inside the datatable toolbar
#                     page.locator("img[src*='excel'], img[title*='Excel'], .ui-commandlink img").first.click()
                
#                 download = download_info.value
#                 out_path = os.path.join(OUTPUT_DIR, f"vahan_fuel_{year}.xlsx")
#                 download.save_as(out_path)
#                 print(f"[OK] Downloaded: {out_path}")
#             except Exception as e:
#                 print(f"[!] Export timed out for {year}: {e}")

#         print("\nAll tasks completed. Closing browser.")
#         browser.close()

# def re_compile_year():
#     import re
#     return re.compile(r"202[0-9]")

# if __name__ == "__main__":
#     run()


import os
import time
from playwright.sync_api import sync_playwright

VAHAN_URL = "https://vahan.parivahan.gov.in/vahan4dashboard/vahan/view/reportview.xhtml"
OUTPUT_DIR = "./vahan_raw_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TARGET_YEARS = ["2026", "2025", "2024", "2023"]

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print(f"Connecting to: {VAHAN_URL}")
        page.goto(VAHAN_URL, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        # 1. Set Y-Axis to 'Fuel' using exact DOM IDs
        print("Configuring Y-Axis -> 'Fuel'...")
        # Open Y-Axis menu
        page.locator("#yaxisVar_label").click()
        page.wait_for_timeout(500)
        
        # Click the exact Y-Axis Fuel option: id="yaxisVar_3"
        page.locator("#yaxisVar_3").click()
        page.wait_for_timeout(2000)

        # 2. Iterate through Target Years and Download
        for year in TARGET_YEARS:
            print(f"\nProcessing Year: {year}...")
            
            # Open Year dropdown
            page.locator("#selectedYear_label").click()
            page.wait_for_timeout(500)
            
            # Click the year inside the selectedYear panel
            page.locator(f"//div[contains(@id, 'selectedYear_panel')]//li[normalize-space(text())='{year}']").click()
            page.wait_for_timeout(1000)

            # Click Refresh button
            print("Refreshing data view...")
            page.locator("button[id*='refresh'], button:has-text('Refresh')").first.click()
            page.wait_for_load_state("networkidle")
            page.wait_for_timeout(4000)

            # Trigger Excel download
            print(f"Downloading dataset for {year}...")
            try:
                with page.expect_download(timeout=25000) as download_info:
                    # Click Excel export icon on the table toolbar
                    page.locator("a[id*='xls'], img[title*='Excel'], .ui-commandlink img").first.click()
                
                download = download_info.value
                out_path = os.path.join(OUTPUT_DIR, f"vahan_fuel_{year}.xlsx")
                download.save_as(out_path)
                print(f"[OK] Downloaded: {out_path}")
            except Exception as e:
                print(f"[!] Export timed out for {year}: {e}")

        print("\nAll downloads completed successfully. Closing browser.")
        browser.close()

if __name__ == "__main__":
    run()