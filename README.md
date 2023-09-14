# AXS Event Webscraper

## Installation
1. Install [python](https://www.python.org/downloads/)
2. Install chrome's [webdriver](https://googlechromelabs.github.io/chrome-for-testing/#stable)

## Usage
```bash
# One input:
python axs-webscraper.py <start> # stops at first 404 error

# Two input:
python axs-webscraper.py <start> <stop>
```

## TODO
- add gui
- async
  - sync -> 1054.10s
  - threadpool -> 444.75s
- automatically download webdriver using `platform.system()` and `platform.machine().endswith('64')`
