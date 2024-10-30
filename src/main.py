import os
from dotenv import load_dotenv
from tiktok_captcha_solver import PlaywrightSolver
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync, StealthConfig
import sys


def test_setup():
    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv('SADCAPTCHA_API_KEY')
    if not api_key:
        print("❌ Error: SADCAPTCHA_API_KEY not found in .env file")
        return

    print("Python version:", sys.version)

    try:
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch(headless=False)
        page = browser.new_page()

        # Configure stealth settings as recommended in the docs
        config = StealthConfig(
            navigator_languages=False,
            navigator_vendor=False,
            navigator_user_agent=False
        )
        stealth_sync(page, config)
        print("✓ Playwright browser initialized successfully")

        solver = PlaywrightSolver(page, api_key)
        print("✓ Solver initialized successfully")
        print("✓ API key loaded successfully")

    except Exception as e:
        print("✗ Setup error:", str(e))
    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    test_setup()
