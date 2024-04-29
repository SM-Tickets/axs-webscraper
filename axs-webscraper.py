import sys
import csv
import time
import datetime

import asyncio
# https://requests.readthedocs.io/projects/requests-html/en/latest/
from requests_html import AsyncHTMLSession
from bs4 import BeautifulSoup

# Open new file
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data_{formatted_datetime}.csv"

sem = asyncio.Semaphore(10)


async def get_response_from_webpage(url, asession):
    """Get the html of a webpage

    Args:
        url (str): URL of webpage
        asession (AsyncHTMLSession): Async HTML session from requests_html lib

    Returns:
        requests.Response: Response object of webpage
    """
    print(f"sending request to {url}")
    r = await asession.get(url)
    print(f"response received for {url}")
    return r



async def render_webpage_response(resp):
    """Render dynamic html by executing the javascript in the initial response from the server

    Args:
        resp (requests.Response): Initial response object of webpage

    Returns:
        requests_html.HTML: HTML object of webpage
    """
    async with sem:
        print(f"rendering html for {resp.url}")
        await resp.html.arender(timeout=0)
        print(f"finished rendering html for {resp.url}")
        return resp.html



async def get_html_of_webpages(urls):
    """Get html of multiple webpages

    Args:
        urls (list[str]): URLs of webpages

    Returns:
        list[requests_html.HTML]: List of HTML objects of webpages
    """

    # GET requests to server
    asession = AsyncHTMLSession()
    request_coros = [get_response_from_webpage(url, asession) for url in urls]
    responses = await asyncio.gather(*request_coros)

    # render javascript
    render_coros = [render_webpage_response(response) for response in responses]
    htmls = await asyncio.gather(*render_coros)
    return htmls



def get_axs_title_from_html(html):
    """Grab the axs title from the html of an axs page

    Args:
        html (requests_html.HTML): HTML object of webpage

    Returns:
        str|None: The title of the axs event if it exists, else None
    """
    axs_title = html.find("h1.series-header__main-title", first=True)

    if axs_title:
        axs_title = axs_title.full_text.strip()  # remove html tags and leading/trailing whitespace

    return axs_title



def get_axs_titles_from_urls(urls):
    """Grab the axs title from an axs URL

    Args:
        urls (list[str]): URLs of webpages

    Returns:
        list[str|None]: The titles of the axs events in corresponding order of the given urls
    """
    htmls = asyncio.run(get_html_of_webpages(urls))

    titles = []
    for html in htmls:
        title = get_axs_title_from_html(html)
        titles.append(title)

    return titles



def axs_id_to_url(id):
    """Get the URL for given axs event ID

    Args:
        id (int): event ID of an axs event

    Returns:
        str: URL of event
    """
    return f"https://www.axs.com/series/{id}/"



def get_axs_titles_from_ids(ids):
    """Grab the axs title for an axs event ID

    Args:
        ids (list[int]): event IDs of axs events

    Returns:
        list[str|None]: The titles of the axs events
    """
    urls = [axs_id_to_url(id) for id in ids]
    titles = get_axs_titles_from_urls(urls)

    return titles



def process_csv(data, filepath, force=False):
    # TODO: actually process file
    print(data)



if __name__ == "__main__":
    # parse cli arguments
    argc = len(sys.argv) - 1
    if argc != 2:
        print(f"Incorrect number of arguments: Expected 2 arguments (start, stop) but received {argc}")
        sys.exit()

    start_id, stop_id = int(sys.argv[1]), int(sys.argv[2])

    # ----- Benchmark start ----- #
    start_time = time.time()

    ids = list(range(start_id, stop_id + 1))
    urls = [axs_id_to_url(id) for id in ids]
    titles = get_axs_titles_from_urls(urls)

    process_csv(titles, "")

    print(time.time() - start_time)
    # ----- Benchmark stop ----- #
