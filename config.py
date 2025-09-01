# config.py
import os

# --- Authentication & Session ---
BASE_URL = "https://hiring.idenhq.com"

# Load credentials securely from environment variables
USERNAME = os.getenv("IDEN_USERNAME")
PASSWORD = os.getenv("IDEN_PASSWORD")

SESSION_FILE = "session.json"


# --- API Interception ---
API_ENDPOINT_PATTERN = "/api/products"


# --- CSS Selectors ---
SELECTORS = {
    # Login Flow
    "username_input": "#email",
    "password_input": "#password",
    "login_button": "button[type='submit']",
    "post_login_element": "button:has-text('Launch Challenge')",
    "dashboard_loaded_element": "button:has-text('Menu')",
    
    # Main navigation selectors
    "menu_button": "button:has-text('Menu')",
    
    # CHANGED: Using more specific text= locators to avoid ambiguity.
    "data_tools_menu": "text=Data Tools",
    "inventory_management_submenu": "text=Inventory Management",
    "product_catalog_link": "text=Product Catalog",
    
    # Button to load the table
    "load_data_button": "button:has-text('Load Product Data')",

    # Product Table
    "product_table_container": ".MuiTableContainer-root"
}