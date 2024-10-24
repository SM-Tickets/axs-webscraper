import os
import subprocess

subprocess.run(["playwright", "install"]) 
# from playwright.__main__ import main as playwright_install
#
# if not os.path.exists(os.path.expanduser("~/.cache/ms-playwright")):
#     playwright_install()

# set PLAYWRIGHT_BROWSERS_PATH manually, since it is 0 by default when run with a pyinstaller binary (https://github.com/microsoft/playwright-python/pull/1002/files)
HOME = os.environ["HOME"]
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = f"{HOME}/Library/Caches/ms-playwright"
