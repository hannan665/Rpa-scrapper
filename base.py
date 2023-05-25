import logging
import os
from abc import abstractmethod, ABC
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Optional, Any

from RPA.Browser.Selenium import Selenium
from RPA.Excel.Files import Files
from RPA.HTTP import HTTP

from base_configs import XPATHS_MAPPER_VARIABLE_NAME, DOWNLOAD_DIRECTORY

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.mkdir(DOWNLOAD_DIRECTORY)


@dataclass
class ElementCallableConfig:
    callable_type: callable
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def call(self, element):
        """
        :param element: WebElement instance

        Apply the WebElement method on element
        Examples:
           element.click()
           element.get_attribute(name)
           element.send_keys(*values)
        """
        self.callable_type(element, *self.args, **self.kwargs)


@dataclass
class BotBrowser:
    url: str

    def open(self):
        """
        Initialize any available browser with RPA selenium.
        :return: selenium instance
        """
        selenium = Selenium()
        selenium.set_download_directory(DOWNLOAD_DIRECTORY)
        selenium.open_available_browser(url=self.url, maximized=True)
        return selenium


@dataclass
class StepConfig:
    """
    Configuration class for step that is going to be taken on browser

    browser_action: A Selenium method to be call
                    browser = Selenium().open_available_browser(url='www.example.com')
                    here: browser_action == browser.find_element
    xpath_name: name of xpath that links to xpath_mapper required param in bot class
    callable_on_element: configuration of dot function on any WebElement instance, not required
    pre_conditions: if it needs any logical work Before browser_action call or override its arguments
    post_conditions: if it needs any logical work immediate After browser_action call and need to manipulate returned data
    args: list of arguments ['a', ] for browser_action
    kwargs: keyword arguments for browser_action
    """
    browser_action: Callable
    xpath_name: str
    callable_on_element: ElementCallableConfig = None
    post_conditions: bool = False
    pre_conditions: bool = False
    args: list = field(default_factory=list)
    kwargs: dict = field(default_factory=dict)

    def apply_step(self, xpath):
        """
        :param xpath: xpath to find an element
        call browser_action with all given arguments
        apply any WebElement function if provided

        :return: WebElement instance
        """

        logger.info(f'xpath_name: {self.xpath_name}, xpath: {xpath}, args: {self.args}, kwargs: {self.kwargs}')
        element = self.browser_action(xpath, *self.args, **self.kwargs)
        if self.callable_on_element and element:
            self.callable_on_element.call(element)
        return element


@dataclass
class ActionConfig:
    action_name: str
    steps_config: list[StepConfig]


class BaseScrapper(ABC):
    """
    Abstract base class.
    actions_config: list for ActionConfigs, the list of steps to be applied on a browser.
    browser: RPA Selenium instance
    """
    actions_config: list[ActionConfig] = []
    browser: Selenium
    files = Files()
    http = HTTP()

    def __init__(self):
        """
        Initialize the required params
        :param params: static data for input to browser
        :param xpaths_mapper: mapping for xpaths, random xpath_name and its value

                              Example:
                              xpath_mapper = {'search_input': '//input[@id="u="random_id"'}

        extra_logic_methods: mapping for methods that are going to be used before or after browser_action, they are required
                             if post_conditions or pre_conditions is enabled in StepConfig, otherwise
                             NotImplementedError exception will be raised

                             IMPORTANT: mapping key should be exact xpath_name provided in a step

                             Example:
                             self.extra_logic_methods = {
                                 'search_input': self.make_text_upper ,
                             }
                             make_text_upper should be defined in subclass


        """
        self.data = set()
        self.xpath_mapper = self.import_variable(var_name=XPATHS_MAPPER_VARIABLE_NAME)
        self.extra_logic_methods: dict = {}

    @property
    @abstractmethod
    def module_name(self):
        """
        Required for importing variables from configs.py
        :return:
        """
        ...

    def import_variable(self, var_name: str) -> Any:
        """
        Imports the variables from configs.py
        :param var_name: variable name to be import from configs.py
        :return: value of variable stored in configs.py
        """
        module_path = f'{self.module_name}.configs'
        module = __import__(module_path, fromlist=[var_name])
        return getattr(module, var_name, None)

    @abstractmethod
    def scrap_data(self):
        """
        Absract method to scrap all the data from web
        """
        ...

    def get_xpath(self, xpath_name: str) -> Optional[str]:
        """
        Get actual xpath from xpath_mapper.
        :param xpath_name: defined in xpath_mapper
        :return: xpath
        """
        if xpath := self.xpath_mapper.get(xpath_name, None):
            return xpath
        raise KeyError(
            f'Xpath Not Found. '
            f'Define xpath in {XPATHS_MAPPER_VARIABLE_NAME} with name: {xpath_name}, '
            f'in {self.module_name}/config')

    def get_extra_logic_method(self, xpath_name) -> callable:
        """

        :param xpath_name: xpath_name for getting the method for extra work based on pre_conditions or post_conditions
        :return: callable
        """
        if xpath_name in self.extra_logic_methods:
            return self.extra_logic_methods.get(xpath_name)
        raise NotImplementedError

    def apply_step(self, step: StepConfig, action: ActionConfig):
        """
        It Applies a step and can be overwritten.

        :param step: StepConfig object
        :param action: ActionConfig object
        """
        step.apply_step(self.get_xpath(step.xpath_name))

    def apply_actions(self):
        """
         Apply all the actions and steps
         It validates if the get_extra_logic_method is provided for a step if any of pre_conditions or post_conditions
         is True
        """
        for action in self.actions_config:
            logger.info(f'============== START ACTION: {action.action_name} ==============')

            for step in action.steps_config:
                logger.info(f'step: {step.browser_action} <<<')
                if step.pre_conditions or step.post_conditions:
                    self.get_extra_logic_method(xpath_name=step.xpath_name)
                self.apply_step(step=step, action=action)
            logger.info(f'============== END ACTION: {action.action_name} ==============')

    def write_excel_file(self):
        """
        It will write data into execl file
        """
        table_data = defaultdict(list)

        for item in self.data:
            for key, value in item:
                table_data[key].append(value)

        if table_data:
            w = self.files.create_workbook(f'{DOWNLOAD_DIRECTORY}/results.xlsx')
            w.append_worksheet("Sheet", table_data, header=True, start=1)
            w.save()

    def start_process(self) -> set:
        """
        It will initialize the bot to apply all actions and steps, scrap data and write to excel file
        :return: scrapped data
        """
        self.apply_actions()
        self.scrap_data()
        self.write_excel_file()
        return self.data
