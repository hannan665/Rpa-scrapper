# Rpa-scrapper

This is a repository for scrapping data from websites, developed with Python [rpaframework](https://rpaframework.org/releasenotes.html).
### Features

1. A structured scrapper developed with python RPA framework. 
3. Easy to use and understandable
4. Applies all RPA.selenium methods with required and non-required arguments
5. It can store all scrapped data into excel file

## [Nytimes](https://www.nytimes.com/)
 1. **Automate Scrap the** [Nytimes](https://www.nytimes.com/)
 2. It will search on specific filters.
 4. It will download the images of the news
 5. It will scrap the news with some details and save it in execl file.
 6. Can be test on [robocorp](https://cloud.robocorp.com/)
 7. All downloaded images and Excel sheets will be land in **output** folder
  
  **Required WorkItmes on Robocop**:


  Keyword | Description
  | :--- | :---
  search_text  | *Search phrase to insert in search field on nytimes (string value)*
  months  | *Number of months (integer value)*
  sections | *A list of sections (eg: ['Arts'])*

  
  **Required variables in** [nytimes-news/configs.py](https://github.com/hannan665/Rpa-scrapper/blob/master/nytimes_news/configs.py) **for local run**:

  Keyword | Description
  | :--- | :---
  SEARCH_TEXT  | *Search phrase to insert in search field on nytimes (string value)*
  MONTHS  | *Number of months (integer value)*
  SECTIONS | *A list of sections (eg: ['Arts'])*


## Setup (using python)
1. *pip install -r requirements.txt*
2. *python run_scrapper.py*

## Setup (using robocorp)

1. [rpaframework](https://rpaframework.org/releasenotes.html)

### Installation

1. Goto [robocorp](https://cloud.robocorp.com/taskoeneg/task/robots) create a bot
2. Add [this](https://github.com/hannan665/Rpa-scrapper.git) repo link in public GIT
3. Goto [assistants](https://cloud.robocorp.com/taskoeneg/task/assistants) and add new assistant linked with robot that you had registered above. 
4. Download and install desktop app of robocorp assistant from [there](https://cloud.robocorp.com/taskoeneg/task/assistants) by click on **Download Robocorp Assistant App**
5. Run the assistant you had created above
6. Bot will start performing the task as mentioned above
7. Your output data will be saved in output folder. click on output when task finished.


## File Structure

### [create_scrapper.py]()
Command to create a new scrapper with 2 built-in files.

````shell
python3 create_scrapper.py new_scrapper
````
**Command name**: _create_scrapper.py_ 
**Argument**: _Scrapper name_

- configs.py 
   
   The file will be generated with required variables.
   Desired variables can be defined here and can be use in scrapper.py

    Keyword | Description
    | :--- | :---
    URL  | *URL of the Website, from where data will be scrapped*
    XPATHS_MAPPER  | *A dict for xpaths. Varaible name can be changed from  [base_config.py](https://github.com/hannan665/Rpa-scrapper/blob/master/base_configs.py).*
- scrapper.py
   
   The file will be genereated having a class with all required functions and params in it.
    ```python
    from base import BaseScrapper, BotBrowser
    from my_new_scrapper.configs import URL
    
    class NewScrapper(BaseScrapper):
        browser = BotBrowser(url=URL).open()
        actions_config = []

        def __init__(self):
            super().__init__()
            self.extra_logic_methods: dict = {}    

        @property
        def module_name(self):
            return 'new_scrapper'

        def scrap_data(self):
           pass
    ```

It will also initialize the newly created scrapper class in [run_scrapper.py](https://github.com/hannan665/Rpa-scrapper/blob/master/run_scrapper.py)

```python
from my_new_scrapper.scrapper import MyNewScrapper
my_new_scrapper_obj = MyNewScrapper()
my_new_scrapper_obj.start_process()
```
    




### [base_configs.py](https://github.com/hannan665/Rpa-scrapper/blob/master/base_configs.py)
This file contains some base variables required in base class.


Keyword | Description
| :--- | :---
XPATHS_MAPPER_NAME  | *xpath mapper varaible name*
DOWNLOAD_DIRECTORY | *Everything will be download in this directory*
ENVIRONMENT | *env variable will be set from robocorp, value would be "PROD"*



### [base.py](https://github.com/hannan665/Rpa-scrapper/blob/master/base.py)
The scrapper base class, it can be used in new scrappers.For NYTimes news using this base class in   [nytimes_scrapper](https://github.com/hannan665/Rpa-scrapper/blob/master/nytimes_scrapper/scrapper.py).
It will initialized the base class and apply all the required funtions and perform base functionality

### [run_scrapper.py](https://github.com/hannan665/Rpa-scrapper/blob/master/run_scrapper.py)
All the scrappers can be initialized here.



command to run:
```shell
python3 run_scrapper.py
```

### [conda.yaml](https://github.com/hannan665/Rpa-scrapper/blob/master/conda.yaml)
Having configuration to set up the environment and [rpaframework](https://rpaframework.org/releasenotes.html) dependencies.

### [robot.yaml](https://github.com/hannan665/Rpa-scrapper/blob/master/conda.yaml)
Having configuration for robocorp to run the [conda.yaml](https://github.com/hannan665/Rpa-scrapper/blob/master/conda.yaml) and execute the task.py


You can find more details and a full explanation of the code on [Robocorp documentation](https://robocorp.com/docs/development-guide/browser/rpa-form-challenge)
