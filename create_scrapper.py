import argparse
import os
from re import sub

from base_configs import XPATHS_MAPPER_VARIABLE_NAME

scrapper_file_content = """from base import BaseScrapper, BotBrowser, ActionConfig
from {scrapper_name}.configs import URL, DOWNLOAD_DIRECTORY


class {class_name}(BaseScrapper):
    browser = BotBrowser(url=URL, download_directory=DOWNLOAD_DIRECTORY).open()
    actions_config: list[ActionConfig] = []
    
    def __init__(self):
        super().__init__()
        self.extra_logic_methods: dict = {{}}    
        
    @property
    def module_name(self):
        return '{scrapper_name}'
    
    def scrap_data(self):
        pass
        
        """

config_file_content = """import os
{XPATHS_MAPPER_VARIABLE_NAME} = {{}}  # please add xpaths 'some_name': '//input[@id=df]'
URL = 'https://www.google.com/'  # required
DOWNLOAD_DIRECTORY = f'{{os.getcwd()}}/{scrapper_name}/output'
"""

runner_file_content = """\nfrom {scrapper_name}.scrapper import {class_name}
{object_name} = {class_name}()
{object_name}.start_process()
"""


def create_scrapper_package():
    parser = argparse.ArgumentParser(description='Create a scrapper package')
    parser.add_argument('scrapper_name', type=str, help='Name of the scrapper')

    args = parser.parse_args()
    scrapper_name = args.scrapper_name
    package_dir = os.path.join(os.getcwd(), scrapper_name)
    os.makedirs(package_dir)

    class_name = ''.join([word.title() for word in sub(r"(_|-)+", " ", scrapper_name).split(' ')])
    if 'Scrapper' not in class_name:
        class_name = class_name + 'Scrapper'

    init_file = os.path.join(package_dir, '__init__.py')
    open(init_file, 'a').close()
    scrapper_file = os.path.join(package_dir, 'scrapper.py')
    with open(scrapper_file, 'w') as file:
        file.write(scrapper_file_content.format(class_name=class_name, scrapper_name=scrapper_name))

    configs_file = os.path.join(package_dir, 'configs.py')
    with open(configs_file, 'w') as file:
        file.write(config_file_content.format(
            XPATHS_MAPPER_VARIABLE_NAME=XPATHS_MAPPER_VARIABLE_NAME,
            scrapper_name=scrapper_name
        ))

    with open('run_scrapper.py', 'a') as f:
        f.write(runner_file_content.format(
            object_name=f'{scrapper_name}_obj',
            class_name=class_name,
            scrapper_name=scrapper_name
        ))
    print('successfully created')


if __name__ == '__main__':
    create_scrapper_package()
