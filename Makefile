build:
	pyinstaller --onefile --add-data "./assets:./assets" axs-webscraper.py

install:
	mv dist/axs-webscraper .

clean:
	rm -rf dist build axs-webscraper.spec

.PHONY: all build install clean
