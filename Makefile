build:
	PLAYWRIGHT_BROWSERS_PATH=./browser_drivers playwright install chromium
	pyinstaller --noconsole --icon ./assets/axs_logo.png --onefile --add-data "./assets:./assets" axs-webscraper.py

install:
	cp -a dist/* .

clean:
	rm -rf dist build axs-webscraper.spec

package:
	bash scripts/package.sh

.PHONY: build install clean package
