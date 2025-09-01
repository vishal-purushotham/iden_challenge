# main.py
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from playwright.async_api import async_playwright, Page, Response, TimeoutError

load_dotenv()

from config import BASE_URL, USERNAME, PASSWORD, SESSION_FILE, SELECTORS, API_ENDPOINT_PATTERN

all_products_data: List[Dict[str, Any]] = []

async def handle_api_response(response: Response):
    if API_ENDPOINT_PATTERN in response.url and response.request.method == "GET":
        print(f"Intercepted API Response from: {response.url}")
        try:
            data = await response.json()
            products = data.get('products', [])
            if products:
                print(f"   -> Found {len(products)} products. Adding to our list.")
                all_products_data.extend(products)
            else:
                print("   -> API response did not contain a 'products' list.")
        except json.JSONDecodeError:
            print(f"   -> Could not decode JSON from {response.url}")

async def login_and_save_session(page: Page):
    print("No valid session found. Performing first-time login...")
    # CORRECTED: This now correctly navigates to the login page.
    await page.goto(BASE_URL) 
    await page.fill(SELECTORS['username_input'], USERNAME)
    await page.fill(SELECTORS['password_input'], PASSWORD)
    await page.click(SELECTORS['login_button'])
    await page.wait_for_selector(SELECTORS['post_login_element'], state="visible", timeout=10000)
    await page.context.storage_state(path=SESSION_FILE)
    print(f"Session state saved to '{SESSION_FILE}'")

async def navigate_to_product_catalog(page: Page):
    print("Navigating to Product Catalog...")
    await page.click(SELECTORS['data_tools_menu'])
    await page.click(SELECTORS['inventory_management_submenu'])
    await page.click(SELECTORS['product_catalog_link'])
    await page.wait_for_selector(SELECTORS['product_table_container'], state="visible")
    print("On the Product Catalog page.")

async def trigger_infinite_scroll(page: Page):
    print("Beginning data extraction via infinite scroll...")
    previous_product_count = -1
    while previous_product_count < len(all_products_data):
        previous_product_count = len(all_products_data)
        print(f"   -> Currently have {len(all_products_data)} products. Scrolling down...")
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except TimeoutError:
            print("   -> Network idle timeout reached, likely at the end of the list.")
            pass
        await page.wait_for_timeout(1000)
    print("Finished scrolling. All data should be captured.")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = None
        if os.path.exists(SESSION_FILE):
            print(f"Session file '{SESSION_FILE}' found. Attempting to reuse.")
            try:
                context = await browser.new_context(storage_state=SESSION_FILE)
                page = await context.new_page()
                # CORRECTED: With a valid session, we go directly to the challenge page.
                await page.goto(f"{BASE_URL}/challenge") 
                await page.wait_for_selector(SELECTORS['post_login_element'], state="visible", timeout=5000)
                print("Session is valid and has been reused.")
            except TimeoutError:
                print("Session is stale or invalid. Proceeding with a fresh login.")
                if context: await context.close()
                context = None

        if not context:
            context = await browser.new_context()
            page = await context.new_page()
            await login_and_save_session(page)

        page.on("response", handle_api_response)
        await navigate_to_product_catalog(page)
        print("   -> Capturing data from initial page load...")
        await page.wait_for_load_state("networkidle", timeout=5000)
        await page.wait_for_timeout(1000)
        await trigger_infinite_scroll(page)
        output_file = 'products.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products_data, f, indent=4, ensure_ascii=False)
        print(f"\nSuccess! Extracted {len(all_products_data)} total products.")
        print(f"Data has been exported to '{output_file}'")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())