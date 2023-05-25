import datetime
import re
from typing import Union, Match
from urllib.parse import urlparse

from SeleniumLibrary.errors import ElementNotFound
from dateutil.relativedelta import relativedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from base import BaseScrapper, ActionConfig, StepConfig, BotBrowser, ElementCallableConfig
from base_configs import DOWNLOAD_DIRECTORY
from nytimes_news.configs import URL, SEARCH_TEXT


class NYTimesNewsScrapper(BaseScrapper):
    browser = BotBrowser(url=URL).open()

    actions_config = [
        ActionConfig(
            action_name='apply_search',
            steps_config=[
                StepConfig(browser.click_button, xpath_name='search_button'),
                StepConfig(browser.input_text, xpath_name='search_input', kwargs={'text': SEARCH_TEXT}),
                StepConfig(browser.click_button, xpath_name='search_submit')
            ]
        ),
        ActionConfig(
            action_name='select_sections',
            steps_config=[
                StepConfig(browser.wait_until_page_contains_element, xpath_name='section_dropdown_btn'),
                StepConfig(
                    browser.find_element,
                    xpath_name='section_dropdown_btn',
                    callable_on_element=ElementCallableConfig(callable_type=WebElement.click)
                ),
                StepConfig(browser.find_elements, xpath_name='section_dropdown_options', post_conditions=True),
                StepConfig(browser.select_from_list_by_value, xpath_name='search_sort_by', args=['newest'])
            ]
        ),
        ActionConfig(
            action_name='apply_date_range',
            steps_config=[
                StepConfig(browser.click_button, xpath_name='date_range_dropdown_btn'),
                StepConfig(browser.click_button, xpath_name='specific_date_btn'),
                StepConfig(browser.input_text, xpath_name='start_date_input', pre_conditions=True),
                StepConfig(browser.input_text, xpath_name='end_date_input', pre_conditions=True),
                StepConfig(browser.press_keys, xpath_name='end_date_input', args=['RETURN'])
            ]
        )
    ]

    def __init__(self, *args, **kwargs):
        """
        Initialize the News bot with required params
        :param args:
        :param kwargs:
        """
        super().__init__()
        self.params = self.import_variable(var_name='PARAMS')
        self.extra_logic_methods: dict = {
            'section_dropdown_options': self._select_sections,
            'start_date_input': self._get_date_range,
            'end_date_input': self._get_date_range
        }

    @property
    def module_name(self):
        return 'nytimes_news'

    @property
    def search_text(self) -> str:
        """
        It will return search text from params that would be defined in config.
        :return: A string
        """
        return self.params.get('search_text', '')

    @property
    def months(self) -> int:
        """
        It will return month from params which would be defined in config.
        :return: A number
        """
        return self.params.get('months', 0)

    @property
    def sections(self) -> list[str]:
        """
        It will return list of sections from params which would be defined in config.
        :return: A list of strings or empty
        """
        return self.params.get('sections', [])

    def click_show_more_button(self):
        """
        click on show more button until page contains
        """
        while True:
            show_more_btn = self.browser.does_page_contain_button(self.get_xpath('show_more_btn'))
            if show_more_btn is None or show_more_btn is False:
                break
            else:
                try:
                    self.browser.scroll_element_into_view(self.get_xpath('show_more_btn'))
                    self.browser.find_element(self.get_xpath('show_more_btn')).click()
                except ElementNotFound:
                    pass

    @staticmethod
    def _check_amount(text: str) -> Union[Match, None]:
        """
        Search dollar amounts from text
        :param text: random string
        :return: matched object or None
        """
        return re.search(r'(\$[\d,]+\.\d{1,2}\b|\d+\sdollars|\d+\sUSD)', text)

    def cookies_popup_accept(self):
        try:
            self.browser.wait_until_page_contains_element(self.get_xpath('cookies_accept_btn'))
            self.browser.click_element_when_visible(self.get_xpath('cookies_accept_btn'))
        except AssertionError:
            pass

    def scrap_data(self):
        """
        Scrap data from web after applying all actions and steps.
        """

        self.cookies_popup_accept()
        self.click_show_more_button()

        for element in self.browser.find_elements(self.get_xpath('search_results')):
            img_link = element.find_element(By.TAG_NAME, 'img')
            image_name = urlparse(img_link.get_attribute('src')).path.split('/')[-1]

            self.http.download(img_link.get_attribute('src'), target_file=DOWNLOAD_DIRECTORY)
            title = element.find_element(By.TAG_NAME, 'h4').text
            description = element.find_elements(By.TAG_NAME, 'p')[1].text

            self.data.add(
                tuple(
                    {
                        'title': title,
                        'description': description,
                        'date': element.find_element(By.TAG_NAME, 'span').text,
                        'picture_name': f'{DOWNLOAD_DIRECTORY}/{image_name}',
                        'search_phrase_in_title': title.count(self.search_text),
                        'search_phrase_in_description': description.count(self.search_text),
                        'is_contains_amount': any([self._check_amount(title), self._check_amount(description)])
                    }.items()
                )
            )

    def _select_sections(self, options: list[WebElement]):
        """
        Apply select sections according to base_configs.py
        :param options: list of elements (WebElement instances)
        """
        for option in options:
            section = option.get_attribute('value').split('|')[0]
            if section in self.sections:
                self.browser.select_checkbox(option)

    def _get_date_range(self, xpath_name: str) -> dict:
        """
        Get start and end date according to the given number of months in base_configs.py
        :param xpath_name: name of xpath, defined in xpath_mapper
        :return a dict of date
        """
        current_date = datetime.date.today()

        start_date = (current_date - relativedelta(months=self.months - 1)).strftime("%m/%d/%Y")
        end_date = current_date.strftime("%m/%d/%Y")
        if self.months < 2:
            start_date = current_date.replace(day=1).strftime("%m/%d/%Y")
        date = {
            'text': start_date
            if xpath_name == 'start_date_input'
            else end_date
        }
        return date

    def apply_step(self, step: StepConfig, action: ActionConfig):
        if step.pre_conditions and step.xpath_name in ['start_date_input', 'end_date_input']:
            step.kwargs = self.get_extra_logic_method(xpath_name=step.xpath_name)(xpath_name=step.xpath_name)

        element = step.apply_step(self.get_xpath(step.xpath_name))

        if step.post_conditions and step.xpath_name == 'section_dropdown_options':
            self.get_extra_logic_method(xpath_name=step.xpath_name)(options=element)
