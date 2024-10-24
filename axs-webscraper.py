import os
import sys
import csv
import time
import datetime
import threading

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


class AxsWebscraper:
    def __init__(self, start_id, stop_id, outfile="", concurrency_limit=10):
        self.start_id = start_id
        self.stop_id = stop_id
        if outfile == "":
            current_datetime = datetime.datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            self.outfile = f"output/{formatted_datetime}.csv"
        else:
            self.outfile = outfile
        self.semaphore = asyncio.Semaphore(concurrency_limit)

        self.ids = list(range(start_id, stop_id + 1))
        self.urls = [self._id_to_url(id) for id in self.ids]

        self.is_running = False

    def _id_to_url(self, id):
        """Get the URL for given axs event ID

        Args:
            id (int): event ID of an axs event

        Returns:
            str: URL of event
        """
        return f"https://www.axs.com/series/{id}/"

    async def _get_html(self, url):
        """Get html for a url

        Args:
          url (str): url to be requested

        Returns:
            dict{str: str}: Mapping of url to raw html
        """
        async with self.semaphore:
            print(f"sending request to {url}")
            async with async_playwright() as pw:
                browser = await pw.chromium.launch()
                page = await browser.new_page()
                await page.goto(url)
                html = await page.content()
                await browser.close()
            print(f"received response from {url}")

        return {url: html}

    async def _get_htmls(self):
        """Get html for urls

        Returns:
            dict{str: BeautifulSoup.BeautifulSoup}: Mapping of urls to BeautifulSoup objects representing the url's corresponding HTML
        """

        coros = [self._get_html(url) for url in self.urls]
        urls_to_raw_htmls = await asyncio.gather(*coros)

        return {url: BeautifulSoup(html, 'html.parser') for url_to_raw_html in urls_to_raw_htmls for url, html in url_to_raw_html.items()}

    def _get_titles(self):
        """Parse the html for the title of the series

        Returns:
            dict{str: str|None}: Mapping of urls to their AXS event titles
        """
        titles = {}
        urls_to_htmls = asyncio.run(self._get_htmls())
        for url, html in urls_to_htmls.items():
            title = html.find('h1', class_='series-header__main-title')
            if title:
                title = title.text.strip()  # remove html tags and leading/trailing whitespace
            titles[url] = title

        return titles

    def run(self, force=False):
        print(f"poop{self.outfile}")
        if self.is_running == False:
            self.is_running = True

            self.urls_to_titles = self._get_titles()
            print(f"\n{self.urls_to_titles}")

            dirname = os.path.dirname(self.outfile)
            if dirname != "" and not os.path.exists(dirname):
                os.makedirs(dirname)

            with open(self.outfile, mode='w') as file:
                file.write(f"URL,Title\n")
                for url, title in self.urls_to_titles.items():
                    file.write(f"{url},{title}\n")

            print(f"\nResult stored in {self.outfile}")

            self.is_running = False


class AxsGui:
    def __init__(self):
        self.is_running = False

        # ROOT
        self.root = tk.Tk()
        self.root.title("AXS Webscraper")

        # START_ID
        self.start_id_label = tk.Label(self.root, text="Start ID:")
        self.start_id_label.pack()
        self.start_id_entry = tk.Entry(self.root)
        self.start_id_entry.pack()

        # STOP_ID
        self.stop_id_label = tk.Label(self.root, text="Stop ID:")
        self.stop_id_label.pack(pady=(10,0))
        self.stop_id_entry = tk.Entry(self.root)
        self.stop_id_entry.pack()

        # FILE SELECTION
        self.filename_label = tk.Label(self.root, text="Filename:")
        self.filename_label.pack(pady=(10,0))

        self.filename_frame = tk.Frame(self.root)
        self.filename_frame.pack(fill=tk.X, padx=50, pady=5)

        self.filename_entry = tk.Entry(self.filename_frame)
        self.filename_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.file_img = Image.open("assets/file.png")
        width, height = self.file_img.size
        self.file_img_resized = self.file_img.resize((width//7, height//7))
        self.file_img_tk = ImageTk.PhotoImage(self.file_img_resized)

        self.select_folder_button = tk.Button(self.filename_frame, image=self.file_img_tk, command=self._select_folder)
        # self.select_folder_button = tk.Button(self.filename_frame, image=self.file_img_tk, command=lambda: print("foo"))
        self.select_folder_button.pack(side=tk.RIGHT, ipadx=2, ipady=2)

        # RUN
        self.run_button = tk.Button(self.root, text="Run", command=lambda: threading.Thread(target=self.scrape).start())
        self.run_button.pack(pady=(10,0))

        # OUTPUT WINDOW
        self.output_label = tk.Label(self.root, text="Output:")
        self.output_label.pack(pady=(30,0))
        self.output_text = tk.Text(self.root, height=20, width=50, state=tk.DISABLED)
        self.output_text.pack(expand=True, fill=tk.X)

        self._connect_stdout_to_output_widget()

    def _connect_stdout_to_output_widget(self):
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, message):
                initial_state = self.text_widget["state"]
                self.text_widget["state"] = tk.NORMAL
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)  # scroll to the end
                self.text_widget["state"] = initial_state
                sys.__stdout__.write(message) # write to original stdout

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.output_text)

    def _select_folder(self):
        folder_selected = filedialog.asksaveasfilename()
        if folder_selected:
            self.filename_entry.delete(0, tk.END)
            self.filename_entry.insert(0, folder_selected)

    @property
    def start_id(self):
        return int(self.start_id_entry.get())

    @property
    def stop_id(self):
        return int(self.stop_id_entry.get())

    @property
    def outfile(self):
        return self.filename_entry.get()

    def scrape(self):
        if not self.is_running:
            self.is_running = True
            start_time = time.time()                           # ----- Benchmark start ----- #

            scraper = AxsWebscraper(self.start_id, self.stop_id, self.outfile)
            scraper.run()
            print("\nFinished scrape")

            print(f"Time elapsed: {time.time() - start_time}") # ----- Benchmark stop ----- #
            self.is_running = False
        else:
            print("\nScrape already in progress\n")

    def run(self):
        self.root.mainloop()

def main():
    # parse cli arguments
    # argc = len(sys.argv) - 1
    # if argc != 2:
    #     print(f"Incorrect number of arguments: Expected 2 arguments (start, stop) but received {argc}")
    #     sys.exit()
    # start_id, stop_id = int(sys.argv[1]), int(sys.argv[2])

    gui = AxsGui()
    gui.run()


if __name__ == "__main__":
    main()
