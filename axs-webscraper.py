import sys
import math
import datetime
import time
import concurrent.futures
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Open new file
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data_{formatted_datetime}.csv"



def get_html_of_webpages(urls):
    """Use selenium to get the html of a webpage (bypasses no-js pages unlike requests lib)

    Args:
        urls (list[str]): URLs of webpages

    Returns:
        list[str]: List of rendered HTML of webpages
    """

    # initialize webdriver
    print("Initializing webdriver...")
    driver = webdriver.Chrome(options=chrome_options)
    print("Webdriver initialized\n")

    htmls = []
    for url in urls:
        print(f"{url}")
        driver.get(url)  # load page with js execution
        htmls.append(driver.page_source)  # store the rendered html
    driver.quit()
    return htmls



def get_axs_title_from_html(html):
    """Grab the axs title from the html of an axs page

    Args:
        html (str): HTML of webpage

    Returns:
        str|None: The title of the axs event if it exists, else None
    """
    soup = BeautifulSoup(html, 'html.parser')  # create a BeautifulSoup object from the html
    axs_title = soup.find('h1', class_='series-header__main-title')

    if axs_title:  # if title exists
        axs_title = axs_title.text.strip()  # remove html tags and leading/trailing whitespace

    return axs_title



def get_axs_titles_from_urls(urls):
    """Grab the axs title from an axs URL

    Args:
        urls (list[str]): URLs of webpages

    Returns:
        list[str|None]: The titles of the axs events
    """
    htmls = get_html_of_webpages(urls)

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



def process_csv(results):
    print(results)



def split_list(l, n_chunks):
    """Split a list into a number of smaller lists

    Args:
        l (list[Any]): List to split
        n_chunks (int): Number of chunks to split into

    Returns:
        list[list[Any]]: The split-up list
    """
    chunk_size = math.ceil(len(l) // n_chunks)
    if n_chunks >= len(l):
        return l
    return [l[i:i + chunk_size] for i in range(0, len(l), chunk_size)]



def get_axs_titles_from_ids_concurrently(start, stop):
    """Get axs titles for events from start to stop (inclusive)

    Args:
        start (int): Event ID of first event
        stop (int): Event ID of last event

    Returns:
        list[tuple[int, title]]: A list of tuples containing the event id and the corresponding title
    """
    ids = list(range(start, stop))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        id_chunks = split_list(ids, executor._max_workers)
        future_to_id = {executor.submit(get_axs_titles_from_ids, id_chunk): id_chunk for id_chunk in id_chunks}

    ids_and_titles = []
    for future in concurrent.futures.as_completed(future_to_id):
        id_chunk = future_to_id[future]
        title_chunk = future.result()
        ids_and_titles.append([id_chunk, title_chunk])

    return ids_and_titles



if __name__ == "__main__":
    # Parse arguments to script
    argc = len(sys.argv) - 1
    if argc != 2:
        print(f"Incorrect number of arguments: Expected 2 arguments (start, stop) but received {argc}")
        sys.exit()

    start_id, stop_id = int(sys.argv[1]), int(sys.argv[2])

    start_time = time.time()

    ids_and_titles = get_axs_titles_from_ids_concurrently(start_id, stop_id)
    process_csv(ids_and_titles)

    print(time.time() - start_time)
