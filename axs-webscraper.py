import sys
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options

argc = len(sys.argv)
if argc not in [2, 3]:
    print(f"Incorrect number of arguments: Expected 1 argument (start) or 2 arguments (start, stop) but received {argc}")
    sys.exit()

if argc == 3:
    start_series, stop_series = int(sys.argv[1]), int(sys.argv[2])
else:
    start_series, stop_series = int(sys.argv[1]), None

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")

# Initialize a Selenium WebDriver (make sure you have the appropriate driver installed)
print("Initializing webdriver...")
driver = webdriver.Chrome(options=chrome_options)
print("Webdriver initialized\n")

# Open new file
current_datetime = datetime.datetime.now()
formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
filename = f"data_{formatted_datetime}.csv"

current_series = start_series
with open(filename, mode='w') as file:
    file.write(f"Series,Title\n")

    while True:
        url = f"https://www.axs.com/series/{current_series}/"

        # Load the page with JavaScript execution
        driver.get(url)

        # Get the fully rendered HTML source after JavaScript execution
        rendered_html = driver.page_source

        # Create a BeautifulSoup object with the rendered HTML
        soup = BeautifulSoup(rendered_html, 'html.parser')

        # Find all the headlines on the page (based on the HTML structure)
        # headlines = soup.find_all('h1')
        headlines = soup.find_all('h1', class_='series-header__main-title')

        # Notify no headlines
        if not headlines:
            print(f"Series {current_series}: NONE")

        # Print the titles of the headlines
        for headline in headlines:
            print(f"Series {current_series}: {headline.text.strip()}")
            file.write(f"{current_series},{headline.text.strip()}\n")

        # Stop condition
        if type(stop_series) == int and (current_series >= stop_series):
            break

        current_series += 1

# Don't forget to close the driver when done
driver.quit()
