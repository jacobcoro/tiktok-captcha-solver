import os
from dotenv import load_dotenv
from tiktok_captcha_solver import PlaywrightSolver
from playwright.sync_api import Page
from playwright.sync_api import Page

load_dotenv()

SADCAPTCHA_API_KEY = os.getenv('SADCAPTCHA_API_KEY')


def main(
    page: Page,
    captcha_detect_timeout: int = 15,
    retries: int = 3
):

    # Initialize captcha solver
    solver = PlaywrightSolver(page, SADCAPTCHA_API_KEY)

    solver.solve_captcha_if_present(
        timeout=captcha_detect_timeout,
        retries=retries
    )
    print("✓ Handled potential captcha")
