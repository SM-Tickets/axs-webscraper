build:
	PLAYWRIGHT_BROWSERS_PATH=./browser_drivers playwright install chromium
	pyinstaller --onefile --add-data "./assets:./assets" axs-webscraper.py

install:
	mv dist/axs-webscraper .

package:
	zip -r axs-webscraper.zip axs-webscraper browser_drivers/

clean:
	rm -rf dist build axs-webscraper.spec

.PHONY: all build install clean
