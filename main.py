# main.py
import asyncio
import json
import os
from dotenv import load_dotenv
from typing import List, Dict, Any

from playwright.async_api import async_playwright, Page, Response, TimeoutError

load_dotenv()

from config import BASE_URL, USERNAME, PASSWORD, SESSION_FILE, SELECTORS, API_ENDPOINT_PATTERN


# This list will store all the product data captured from API responses
all_products_data: List[Dict[str, Any]] = []


async def handle_api_response(response: Response):
    """Intercepts API calls to grab product data directly."""
    if API_ENDPOINT_PATTERN in response.url and response.request.method == "GET":
        print(f"Intercepted API Response from: {response.url}")
        try:
            data = await response.json()
            products = data.get('products', [])
            if products:
                print(f"   -> Found {len(products)} products. Adding to our list.")
                all_products_data.extend(products)
        except json.JSONDecodeError:
            print(f"   -> Could not decode JSON from {response.url}")


async def login_and_save_session(page: Page):
    """Performs the initial login and saves the session."""
    print("No valid session found. Performing first-time login...")
    await page.goto(BASE_URL) 
    await page.fill(SELECTORS['username_input'], USERNAME)
    await page.fill(SELECTORS['password_input'], PASSWORD)
    await page.click(SELECTORS['login_button'])
    await page.wait_for_selector(SELECTORS['post_login_element'], state="visible", timeout=10000)
    await page.context.storage_state(path=SESSION_FILE)
    print("Session state saved.")


async def navigate_to_product_catalog(page: Page):
    """Navigates the complex menu to the product table and loads the data."""
    print("Navigating complex menu to Product Catalog...")
    await page.click(SELECTORS['menu_button'])
    await page.click(SELECTORS['data_tools_menu'])
    await page.click(SELECTORS['inventory_management_submenu'])
    await page.click(SELECTORS['product_catalog_link'])
    print("On Product Catalog page, clicking 'Load Product Data'...")
    await page.wait_for_selector(SELECTORS['load_data_button'], state="visible")
    await page.click(SELECTORS['load_data_button'])
    await page.wait_for_selector(SELECTORS['product_table_container'], state="visible")
    print("Product data table is loaded.")


async def trigger_infinite_scroll(page: Page):
    """
    REWRITTEN: Scrolls by hovering over the table and using the mouse wheel,
    which is the most reliable method for custom scroll containers.
    """
    print("Beginning data extraction via infinite scroll...")
    previous_product_count = -1
    
    # Locate the scrollable table container once
    table_container = page.locator(SELECTORS['product_table_container'])

    while previous_product_count < len(all_products_data):
        previous_product_count = len(all_products_data)
        print(f"   -> Currently have {len(all_products_data)} of 1920 products. Scrolling...")

        # Step 1: Hover over the table to ensure it has mouse focus
        await table_container.hover()
        
        # Step 2: Use the mouse wheel to scroll down, simulating a user action.
        # A large deltaY value ensures a significant scroll.
        await page.mouse.wheel(0, 15000)
        
        try:
            # Wait for any new network requests to complete after scrolling
            await page.wait_for_load_state("networkidle", timeout=5000)
        except TimeoutError:
            print("   -> Network idle timeout reached. This is expected at the end of the list.")
            pass
        
        # A static wait to ensure the UI has time to update
        await page.wait_for_timeout(1500)

    print("Finished scrolling. All data captured.")


async def main():
    """Main function to orchestrate the automation process."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False) # Set to False to watch it run
        context = None
        if os.path.exists(SESSION_FILE):
            print(f"Session file found. Attempting to reuse.")
            try:
                context = await browser.new_context(storage_state=SESSION_FILE)
                page = await context.new_page()
                await page.goto(f"{BASE_URL}/instructions") 
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

        print("On instructions page, clicking 'Launch Challenge'...")
        await page.click(SELECTORS['post_login_element'])

        print("Waiting for dashboard to load...")
        await page.wait_for_selector(SELECTORS['dashboard_loaded_element'], state="visible")
        print("Dashboard loaded.")

        page.on("response", handle_api_response)

        await navigate_to_product_catalog(page)
        
        print("Capturing data from initial page load...")
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