# Iden Challenge - Product Data Scraper

This repository contains a high-performance Python script for the Iden Challenge. The solution automates the process of extracting product data from a web application, handling session management and dynamic content loading efficiently.

## Key Features

- **High-Performance Scraping**: Intercepts background API (XHR) calls to grab raw JSON data directly, avoiding slow UI rendering and HTML parsing.
- **Robust Session Management**: Automatically saves the login session to a `session.json` file. Subsequent runs reuse the session, skipping the login process entirely.
- **Infinite Scroll Handling**: Intelligently handles dynamically loaded content by scrolling the page until all products have been loaded and captured.
- **Clean & Configurable**: The script is well-structured, with credentials, URLs, and selectors stored in a separate `config.py` file for easy maintenance.
- **Structured Output**: All extracted product data is saved to a clean, well-formatted `products.json` file.

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd <repository-folder>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install
   ```

## How to Run

Execute the main script from the terminal. The first run will perform a login and create a `session.json` file. Subsequent runs will be much faster as they will reuse the saved session.

```bash
python main.py
```

Upon completion, the script will generate a `products.json` file in the project root containing all the extracted product data.