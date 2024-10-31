import sentry_sdk
import os
from dotenv import load_dotenv
import logging
from playwright.sync_api import Page
from typing import Optional
from aws import ScreenshotStorage

load_dotenv()
SENTRY_DSN = os.getenv('SENTRY_DSN')
IS_PROD = os.getenv('ENVIRONMENT') == 'production'


def init_sentry():
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=1.0,
    )


def handle_scraper_exception(e, page: Page, config,  take_debug_screens: bool = True):
    if (not IS_PROD):
        logging.error(f"Exception occurred: {e}")
        return

    picture_name = f"OutreachMessageBot-FAILED-{config.get(
        'agency_campaign_id', 'unknown')}-{config['creator']}"
    picture_url = ''
    if take_debug_screens:
        picture_url = take_debug_screenshot(page, picture_name)
        logging.error(
            f"OutreachMessageBot interrupted due to a missing element. screenshot link: {picture_url}")

    with sentry_sdk.push_scope() as scope:
        if take_debug_screens:
            scope.set_extra('pictureURL', picture_url)
        sentry_sdk.capture_exception(e)
        logging.error(f"Exception captured: {e}")


def take_debug_screenshot(page: Page, name: str) -> Optional[str]:
    """Take debug screenshot if enabled"""
    screenshot_bytes = page.screenshot()
    storage = ScreenshotStorage()
    return storage.save_screenshot(screenshot_bytes, name)
