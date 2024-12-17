build:
	PLAYWRIGHT_BROWSERS_PATH=./browser_drivers playwright install chromium
	pyinstaller --noconsole --icon ./assets/axs_logo.png --onefile --add-data "./assets:./assets" axs-webscraper.py

install:
	if [ -e dist/axs-webscraper ]; then cp dist/axs-webscraper .; fi
	if [ -e dist/axs-webscraper.app ]; then rm -rf axs-webscraper.app; cp -a dist/axs-webscraper.app .; fi

package:
	if [ "$$(uname -o)" = "Darwin" ]; then zip -r axs-webscraper.zip axs-webscraper.app browser_drivers/; fi
	if [ "$$(uname -o)" = "Msys" ]; then zip -r axs-webscraper.zip axs-webscraper.exe browser_drivers/; fi

clean:
	rm -rf dist build axs-webscraper.spec

.PHONY: all build install clean
