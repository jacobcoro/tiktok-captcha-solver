from playwright.sync_api import Page
from logger import get_logger

# Get a logger instance
logger = get_logger(__name__)


def set_business_cookies(page: Page, seller_session_id: str, web_id: str) -> None:
    """
    Set required business cookies for TikTok scraping

    Args:
        page (Page): Playwright page instance
        seller_session_id (str): TikTok seller session ID
        web_id (str): TikTok web ID
    """
    logger.info('Starting setBusinessCookies...')
    logger.debug(f'setBusinessCookies() params: seller_session_id={
        seller_session_id}, web_id={web_id}')

    saved_cookies = [
        {
            'name': 'sessionid_ss_tiktokseller',
            'value': seller_session_id,
            'domain': '.tiktok.com',
            'path': '/',
        },
        {
            'name': 's_v_web_id',
            'value': web_id,
            'domain': '.tiktok.com',
            'path': '/',
        },
        {
            'name': 'i18next',
            'value': 'en',
            'domain': '.tiktok.com',
            'path': '/',
        }
    ]

    context = page.context
    for cookie in saved_cookies:
        context.add_cookies([{
            'name': cookie['name'],
            'value': cookie['value'],
            'domain': cookie.get('domain'),
            'path': cookie.get('path', '/'),
        }])
