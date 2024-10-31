import os
from dotenv import load_dotenv
from tiktok_captcha_solver import PlaywrightSolver
from playwright.sync_api import Page
from playwright.sync_api import Page
from logger import get_logger

logger = get_logger(__name__)

load_dotenv()

SADCAPTCHA_API_KEY = os.getenv('SADCAPTCHA_API_KEY')


def main(
    page: Page,
    captcha_detect_timeout: int = 15,
    retries: int = 2
):
    if not page.is_visible('body'):
        logger.warning("Page is not visible, skipping captcha solving")
        return

    if not page.is_visible("text=Select 2 objects that are the same shape"):
        logger.warning("Captcha not detected, skipping captcha solving")
        return

    logger.debug("Starting captcha solver")
    # Initialize captcha solver
    solver = PlaywrightSolver(page, SADCAPTCHA_API_KEY)
    logger.debug("Initialized captcha solver")
    solver.solve_captcha_if_present(
        captcha_detect_timeout=captcha_detect_timeout,
        retries=retries
    )
    logger.debug("✓ Handled potential captcha")
