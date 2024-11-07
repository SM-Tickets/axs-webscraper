build:
	playwright install chromium
	pyinstaller --onefile --add-data "./assets:./assets" --runtime-hook scripts/pyinstaller_hook.py axs-webscraper.py

install:
	mv dist/axs-webscraper .

clean:
	rm -rf dist build axs-webscraper.spec

.PHONY: all build install clean
