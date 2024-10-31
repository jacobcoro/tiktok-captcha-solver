from .solve_captcha import main as solve_captcha
from playwright.sync_api import sync_playwright, Page
from playwright_stealth import stealth_sync, StealthConfig
import time
import logging
from playwright.sync_api import Page


LOGIN_URL = "https://seller-us-accounts.tiktok.com/account/login"


def setup_page(page: Page) -> None:
    """Configure stealth settings and timeout"""
    config = StealthConfig(
        navigator_languages=False,
        navigator_vendor=False,
        navigator_user_agent=False
    )
    stealth_sync(page, config)
    page.set_default_timeout(30000)  # 30 second timeout


def login_to_tiktok(page: Page, email: str, password: str) -> None:
    """Perform login sequence"""
    try:
        # Navigate to login page
        page.goto(LOGIN_URL)
        logging.info("✓ Navigated to login page")

        # Wait for and click email tab using role
        email_tab = page.get_by_role("tab", name="Email")
        email_tab.click()
        logging.info("✓ Clicked email tab")

        # Find input fields by type and placeholder text
        email_input = page.get_by_role(
            "textbox", name="Enter your email address")
        email_input.fill(email)
        logging.info("✓ Entered email")

        password_input = page.get_by_role(
            "textbox", name="Enter your password")
        password_input.fill(password)
        logging.info("✓ Entered password")

        # Click login button by role
        login_button = page.get_by_role("button", name="Log in", exact=True)
        login_button.click()
        logging.info("✓ Clicked login button")

        # Wait a moment for captcha to appear and solve if present
        time.sleep(2)  # Give time for captcha to appear
        solve_captcha(Page)
        logging.info("✓ Handled potential captcha")

        # Wait for navigation after successful login
        page.wait_for_load_state('networkidle')
        logging.info("✓ Login sequence completed")

        # TODO: Get auth code from email and fill it in
        # TODO: Save and return cookies

    except Exception as e:
        logging.info(f"✗ Error during login: {str(e)}")
        raise


def main(email: str, password: str):
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        # headless=False,  # Show the browser
        # slow_mo=100,     # Slow down actions for debugging
    )

    context = browser.new_context(viewport={'width': 1280, 'height': 800})

    page = context.new_page()
    setup_page(page)

    try:
        login_to_tiktok(page, email, password)

        # Keep the browser open for inspection
        # input("Press Enter to close the browser...")
    except Exception as e:
        logging.info(f"Fatal error: {str(e)}")
    finally:
        browser.close()
        playwright.stop()


if __name__ == "__main__":
    """_summary_ Login to TikTok seller center and fetch cookies.
    Args:
        email (str): Seller center email
        password (str): Seller center password

    Usage:
        python login.py --email your_email --password your_password
    """
    import argparse
    parser = argparse.ArgumentParser(
        description='Login and fetch cookies.')
    parser.add_argument('--email', required=True,
                        help='Seller center email')
    parser.add_argument('--password', required=True,
                        help='Seller center password')
    args = parser.parse_args()
    main(args.email, args.password)
