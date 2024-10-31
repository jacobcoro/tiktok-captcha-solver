from os import getenv

from playwright.sync_api import Page, TimeoutError, Error
from logger import get_logger

logger = get_logger(__name__)

FIND_CREATOR_URL = 'https://affiliate-us.tiktok.com/connection/creator?shop_region=US'
TAKE_DEBUG_SCREENS = True


class OutreachMessageBot:
    def __init__(self, page: Page):
        self.page = page

    def execute(self, config: dict) -> dict:
        """Execute the outreach message task"""
        logger.info(f"Run OutreachMessageBot for creator: '{
            config['creator']}'")

        self.find_creator(config['creator'])
        self.process_messages(config['message'])

        return {}

    def find_creator(self, creator: str) -> None:
        """Find and navigate to creator's page"""
        if not creator:
            logger.warning(
                'Encountered a creator without a tiktok_username, this task will not be executed')
            return

        logger.info('findCreator ...')
        self.page.goto(FIND_CREATOR_URL)
        self.skip_modal()

        try:
            if not self.check_language():
                self.page.reload()
                if not self.check_language():
                    raise Exception(
                        'Oops! This is not the English page, please try again later')
        except TimeoutError:
            current_url = self.page.url
            if current_url != FIND_CREATOR_URL:
                cookies = self.page.context.cookies()
                raise Exception(f'Detected an incorrect redirect to: {
                                current_url}. cookies: {cookies}')

        logger.info('Successfully entered the creators page.')

        # Search for creator
        self.page.wait_for_selector(
            'input[placeholder="Search names, products, hashtags, or keywords"]', timeout=10000)
        search_input = self.page.locator(
            'input[placeholder="Search names, products, hashtags, or keywords"]')
        search_input.fill(creator)
        search_input.press('Enter')

        # Wait for and click first result
        self.page.wait_for_selector(
            '.arco-table-tr.arco-table-empty-row', state='hidden', timeout=10000)
        first_cell = self.page.locator(
            '.arco-table-body tbody tr:first-child td:first-child')
        first_cell.click()
        self.move_to_next_plan()
        logger.info('Successfully entered the creator details page.')

        # Find and click message icon
        self.page.wait_for_selector('.alliance-icon-Message', timeout=15000)
        self.page.evaluate("""
            const messageButton = document.querySelector('.alliance-icon-Message').closest('button, a, [onclick]');
            if (messageButton) {
                const reactPropsKey = Object.keys(messageButton).find(key => key.startsWith('__reactProps$'));
                const reactProps = messageButton[reactPropsKey];
                if (reactProps && typeof reactProps.onClick === 'function') {
                    reactProps.onClick({
                        preventDefault: () => {},
                        stopPropagation: () => {}
                    });
                }
            }
        """)

        self.move_to_next_plan()

    def process_messages(self, message: str) -> None:
        """Process and send messages to creator"""
        logger.info('processMessages ...')
        self.page.wait_for_selector(
            'div#im_sdk_ui_sdk_message_box', timeout=15000)
        logger.info('Successfully entered the chat page.')

        self.page.wait_for_selector('textarea')
        self.skip_tip()

        try:
            textarea = self.page.locator('textarea').first
            textarea.fill(message)

            # Only click send in production
            if self.is_production():
                self.page.locator('button.arco-btn-primary').first.click()

        except Error as e:
            logger.warning('Element not found or timeout occurred')
            if TAKE_DEBUG_SCREENS:
                self.take_debug_screenshot('SEND_MESSAGE_FAIL')
            raise  # Re-raise the exception

        self.take_debug_screenshot('BIG_SUCCESS')
        logger.info('Complete mission.')

    def skip_modal(self) -> None:
        """Skip modal if present"""
        try:
            modal = self.page.wait_for_selector(
                '.arco-modal-mask', timeout=10000)
            logger.info('Catch the modal!')
            self.page.evaluate(
                '(element) => element.parentNode.remove()', modal)
        except Error:
            pass

    def skip_tip(self) -> None:
        """Skip tutorial/welcome tip if present"""
        try:
            skip_button = self.page.wait_for_selector('//span[text()="Skip"]/parent::button',
                                                      timeout=10000)
            if TAKE_DEBUG_SCREENS:
                self.take_debug_screenshot('ENCOUNTERING-SKIP-GUIDE')
            if skip_button:
                skip_button.click()
        except TimeoutError:
            pass

    def move_to_next_plan(self) -> None:
        """Switch to the latest browser window/tab"""
        pages = self.page.context.pages
        if pages:
            self.page = pages[-1]

    def check_language(self) -> bool:
        """Check if page is in English"""
        logger.info('checkLanguage ...')
        try:
            title_element = self.page.wait_for_selector(
                '.m4b-page-header-title-text')
            title_text = title_element.text_content()
            is_english = title_text == 'Find creators'

            if not is_english and TAKE_DEBUG_SCREENS:
                self.take_debug_screenshot('LOCALIZATION-ISSUES')

            return is_english
        except Error:
            return False

    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment"""
        return getenv('ENVIRONMENT') == 'production'
