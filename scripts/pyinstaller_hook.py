import os

# set PLAYWRIGHT_BROWSERS_PATH manually, since it is 0 by default when run with a pyinstaller binary (https://github.com/microsoft/playwright-python/pull/1002/files)
HOME = os.environ["HOME"]
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/Library/Caches/ms-playwright"
