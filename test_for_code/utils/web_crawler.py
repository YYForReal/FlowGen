# metagpt/tools/libs/web_scraper.py
import requests
from metagpt.tools.tool_registry import register_tool


@register_tool(tags=["web","firecrawl"], include_functions=["__init__", "scrape_website"])
class WebScraper:
    """
    A tool for scraping websites and extracting specific content.
    """

    def __init__(self, base_url="http://192.168.31.136:3002/v0/scrape", api_key=""):
        """
        Initialize the WebScraper.
        """
        self.base_url = base_url
        self.api_key = api_key

    def scrape_website(
        self,
        target_url,
        only_main_content=True,
        include_html=True,
        include_raw_html=False,
        screenshot=False,
        wait_for=300,
    ):
        """
        Scrapes a website with the given parameters.

        Args:
            target_url (str): The URL of the website to be scraped.

        Returns:
            dict: The JSON response from the API if the request is successful. keys are 'content', 'markdown',  'html', 'metadata'.
            str: An error message if the request fails. 'Request failed! ...'
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        data = {
            "url": target_url,
            "pageOptions": {
                "onlyMainContent": only_main_content,
                "includeHtml": include_html,
                "includeRawHtml": include_raw_html,
                "screenshot": screenshot,
                "waitFor": wait_for,
                "onlyIncludeTags": [
                    "#mainContent",
                    "#maincontent",
                    "#main-content",
                    "#course",
                    ".mainContent",
                    ".maincontent",
                    ".main-content",
                    "main",
                    "#content",
                    ".main-content",
                    ".content",
                    "article",
                ],
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
                "removeTags": [
                    "script",
                    "style",
                    "noscript",
                    "iframe",
                    "svg",
                    "ins",
                    "#course",
                    ".tiy"
                ],  # #course is a custom tag to remove
            },
        }

        response = requests.post(self.base_url, headers=headers, json=data)

        if response.status_code == 200:
            print("WebScraper: Website scraped successfully!")
            print(response.json()["data"]["metadata"])
            return response.json()["data"]
        else:
            return f"Request failed! Status code: {response.status_code}, Response text: {response.text}"
