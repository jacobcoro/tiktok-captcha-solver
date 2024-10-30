import os
from dotenv import load_dotenv
from tiktok_captcha_solver import PlaywrightSolver
from playwright.sync_api import sync_playwright, Page
from playwright_stealth import stealth_sync, StealthConfig
import time

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
LOGIN_URL = "https://seller-us-accounts.tiktok.com/account/login"

SADCAPTCHA_API_KEY = os.getenv('SADCAPTCHA_API_KEY')


def setup_page(page: Page) -> None:
    """Configure stealth settings and timeout"""
    config = StealthConfig(
        navigator_languages=False,
        navigator_vendor=False,
        navigator_user_agent=False
    )
    stealth_sync(page, config)
    page.set_default_timeout(30000)  # 30 second timeout


def login_to_tiktok(page: Page) -> None:
    """Perform login sequence"""
    try:
        # Navigate to login page
        page.goto(LOGIN_URL)
        print("✓ Navigated to login page")

        # Wait for and click email tab using role
        email_tab = page.get_by_role("tab", name="Email")
        email_tab.click()
        print("✓ Clicked email tab")

        # Find input fields by type and placeholder text
        email_input = page.get_by_role(
            "textbox", name="Enter your email address")
        email_input.fill(EMAIL)
        print("✓ Entered email")

        password_input = page.get_by_role(
            "textbox", name="Enter your password")
        password_input.fill(PASSWORD)
        print("✓ Entered password")

        # Click login button by role
        login_button = page.get_by_role("button", name="Log in", exact=True)
        login_button.click()
        print("✓ Clicked login button")

        # Initialize captcha solver
        solver = PlaywrightSolver(page, SADCAPTCHA_API_KEY)

        # Wait a moment for captcha to appear and solve if present
        time.sleep(2)  # Give time for captcha to appear
        solver.solve_captcha_if_present()
        print("✓ Handled potential captcha")

        # Wait for navigation after successful login
        page.wait_for_load_state('networkidle')
        print("✓ Login sequence completed")

    except Exception as e:
        print(f"✗ Error during login: {str(e)}")
        raise


def main():

    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        # headless=False,  # Show the browser
        # slow_mo=100,     # Slow down actions for debugging
    )

    context = browser.new_context(
        viewport={'width': 1280, 'height': 800}
    )

    page = context.new_page()
    setup_page(page)

    try:
        login_to_tiktok(page)

        # Keep the browser open for inspection
        input("Press Enter to close the browser...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()
