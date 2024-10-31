import logging
from playwright.sync_api import sync_playwright
from .solve_captcha import main as solve_captcha
from .set_cookies import set_business_cookies
from playwright.sync_api import sync_playwright, Page
from playwright_stealth import stealth_sync, StealthConfig
import logging
from playwright.sync_api import Page

TAKE_DEBUG_SCREENS = True


def setup_page(page: Page):
    """Configure stealth settings and timeout"""
    config = StealthConfig(
        navigator_languages=False,
        navigator_vendor=False,
        navigator_user_agent=False
    )
    stealth_sync(page, config)
    page.set_default_timeout(30000)  # 30 second timeout


def send_message(page: Page, message, tiktok_account):
    """Send a message to a TikTok creator"""
    logging.info('Sending message...')
    page.goto(f'https://www.tiktok.com/@{tiktok_account}/message')
    page.fill('textarea', message)
    page.click('button[type="submit"]')
    logging.info('Message sent!')


def retry_with_captchas(page: Page, message, tiktok_account, retries=3):
    for attempt in range(retries):
        try:
            send_message(page, message, tiktok_account)
            break  # Exit loop if message sent successfully
        except Exception as e:
            logging.error(f'Error occurred while sending message: {e}')
            if TAKE_DEBUG_SCREENS:
                page.screenshot(path=f'error_screenshot_{attempt}.png')
            if attempt < retries - 1:
                logging.info('Retrying...')
                solve_captcha(page)


def main(sessionid_cookie, web_id_cookie, message, tiktok_account):
    with sync_playwright() as p:
      # if a captcha error is encountered, use the captcha solver and try again
        browser = p.chromium.launch()
        page = browser.new_page()
        setup_page(page)
        set_business_cookies(page, sessionid_cookie, web_id_cookie)
        retry_with_captchas(page, message, tiktok_account)
        browser.close()


if __name__ == "__main__":
    """_summary_ Send a message to creator from the affiliate/seller center.
    Args:
        sessionid_cookie (str): Session ID cookie value
        web_id_cookie (str): Web ID cookie value
        message (str): Message to send
        tiktok_account (str): Name of the creator TikTok account not including @
        _example: python send_message.py --sessionid_cookie <sessionid> --web_id_cookie <web_id> --message <message> --tiktok_account <tiktok_account>
    """
    import argparse
    parser = argparse.ArgumentParser(
        description='Send message using cookies.')
    parser.add_argument('--sessionid_cookie',
                        required=True, help='Session ID cookie value')
    parser.add_argument('--web_id_cookie', required=True,
                        help='Web ID cookie value')
    parser.add_argument('--message', required=True, help='Message to send')
    parser.add_argument('--tiktok_account', required=True,
                        help='Name of the creator TikTok account not including @')
    args = parser.parse_args()
    main(args.sessionid_cookie, args.web_id_cookie,
         args.message, args.tiktok_account)
