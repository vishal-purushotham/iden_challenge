# config.py
# --- Authentication & Session ---
# CORRECTED: BASE_URL now points to the root domain.
USERNAME = os.getenv("IDEN_USERNAME")
PASSWORD = os.getenv("IDEN_PASSWORD")
SESSION_FILE = "session.json"

# --- API Interception ---
API_ENDPOINT_PATTERN = "/api/products"

# --- CSS Selectors ---
SELECTORS = {
    "username_input": "#email",
    "password_input": "#password",
    "login_button": "button[type='submit']",
    "post_login_element": "button:has-text('Submit Script')",
    "data_tools_menu": "div:has-text('Data Tools')",
    "inventory_management_submenu": "div:has-text('Inventory Management')",
    "product_catalog_link": "a:has-text('Product Catalog')",
    "product_table_container": ".MuiTableContainer-root",
    "next_page_button": "button[aria-label='Go to next page']"
}