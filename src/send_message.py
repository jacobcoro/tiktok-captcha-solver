from os import getenv
from solve_captcha import main as solve_captcha
from set_cookies import set_business_cookies
from playwright.sync_api import sync_playwright, Page
from playwright_stealth import stealth_sync, StealthConfig
from sentry import init_sentry, handle_scraper_exception
from outreach_bot import OutreachMessageBot
from logger import get_logger

logger = get_logger(__name__)

IS_PROD = getenv('ENVIRONMENT') == 'production'
TAKE_DEBUG_SCREENS = IS_PROD


def setup_page(page: Page):
    """Configure stealth settings and timeout"""
    config = StealthConfig(
        navigator_languages=False,
        navigator_vendor=False,
        navigator_user_agent=False
    )
    stealth_sync(page, config)
    page.set_default_timeout(30000)  # 30 second timeout


def retry_with_captchas(page: Page, message: str, tiktok_account: str, agency_campaign_id: str, retries=3):
    config = {
        'creator': tiktok_account,
        'agency_campaign_id': agency_campaign_id,
        'message': message
    }
    bot = OutreachMessageBot(page)

    for attempt in range(retries):
        try:
            bot.execute(config)
            break  # Exit loop if message sent successfully
        except Exception as e:
            handle_scraper_exception(
                e, page, {'creator': tiktok_account}, TAKE_DEBUG_SCREENS)
            if attempt < retries - 1:
                logger.info('Retrying...')
                solve_captcha(page)


def main(sessionid_cookie: str, web_id_cookie: str, message: str, tiktok_account: str, agency_campaign_id: str):
    with sync_playwright() as p:
      # if a captcha error is encountered, use the captcha solver and try again
        browser = p.chromium.launch(
            headless=IS_PROD
        )
        page = browser.new_page()
        setup_page(page)
        set_business_cookies(page, sessionid_cookie, web_id_cookie)
        retry_with_captchas(page, message, tiktok_account, agency_campaign_id)
        logger.info('Finished sending message.')
        if (IS_PROD):
            browser.close()
        else:
            # keeps script running to leave open in debug to see results
            input("Press Enter to close the browser...")


if __name__ == "__main__":
    """_summary_ Send a message to creator from the affiliate/seller center.
    Args:
        sessionid_cookie (str): Session ID cookie value
        web_id_cookie (str): Web ID cookie value
        message (str): Message to send
        tiktok_account (str): Name of the creator TikTok account not including @
        agency_campaign_id (str): Agency campaign ID

    Usage example: python send_message.py --sessionid_cookie <sessionid> --web_id_cookie <web_id> --message <message> --tiktok_account <tiktok_account> --agency_campaign_id <agency_campaign_id>
    """
    init_sentry()
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
    parser.add_argument('--agency_campaign_id',
                        required=True, help='Agency campaign ID')
    args = parser.parse_args()
    main(args.sessionid_cookie, args.web_id_cookie,
         args.message, args.tiktok_account, args.agency_campaign_id)
