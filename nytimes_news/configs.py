import os

SEARCH_TEXT = 'Covid pakistan'
SECTIONS = ['Books', 'Business', 'New York']
MONTHS = 30
URL = 'https://www.nytimes.com/'

XPATHS_MAPPER = {
    'search_button': '//button[@data-test-id="search-button"]',
    'search_input': '//input[@data-testid="search-input"]',
    'search_submit': '//button[@data-test-id="search-submit"]',
    'section_dropdown_btn': '//button[@data-testid="search-multiselect-button"]/label[text()="Section"]',
    'section_dropdown_options': '//input[@data-testid="DropdownLabelCheckbox"]',
    'search_sort_by': '//select[@data-testid="SearchForm-sortBy"]',
    'search_results': '//ol/li[@data-testid="search-bodega-result"]/div',
    'show_more_btn': '//button[@data-testid="search-show-more-button"]',
    'date_range_dropdown_btn': '//button[@data-testid="search-date-dropdown-a"]',
    'specific_date_btn': '//button[@value="Specific Dates"]',
    'end_date_input': '//input[@id="endDate"]',
    'start_date_input': '//input[@id="startDate"]',
}

PARAMS = {
    'search_text': SEARCH_TEXT,
    'sections': SECTIONS,
    'months': MONTHS
}
DOWNLOAD_DIRECTORY = f'{os.getcwd()}/nytimes_news/output'