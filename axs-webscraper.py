import sys
import csv
import time

import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

import asyncio
from requests_html import AsyncHTMLSession # https://requests.readthedocs.io/projects/requests-html/en/latest/


class AxsWebscraper:
    def __init__(self, start_id, stop_id, outfile=None, concurrency_limit=10):
        self.start_id = start_id
        self.stop_id = stop_id
        self.outfile = outfile
        self.semaphore = asyncio.Semaphore(concurrency_limit)

        self.ids = list(range(start_id, stop_id + 1))
        self.urls = [self._id_to_url(id) for id in self.ids]
        self.htmls = asyncio.run(self._get_html())
        self.titles = self._get_titles()

    def _id_to_url(self, id):
        """Get the URL for given axs event ID

        Args:
            id (int): event ID of an axs event

        Returns:
            str: URL of event
        """
        return f"https://www.axs.com/series/{id}/"

    async def _get_webpage_response(self, url, asession):
        """Get the response object of a webpage

        Args:
            url (str): URL of webpage

        Returns:
            requests.Response: Response object of webpage
        """
        print(f"sending request to {url}")
        r = await asession.get(url)
        print(f"response received for {url}")
        return r

    async def _render_webpage_response(self, resp):
        """Render dynamic html by executing the javascript in the initial response from the server

        Args:
            resp (requests.Response): Initial response object of webpage

        Returns:
            requests_html.HTML: HTML object of webpage
        """
        async with self.semaphore:
            print(f"rendering html for {resp.url}")
            await resp.html.arender(timeout=0)
            print(f"finished rendering html for {resp.url}")
            return resp.html

    async def _get_html(self):
        """Get html for urls

        Returns:
            list[requests_html.HTML]: List of HTML objects of webpages
        """

        # initial requests to server
        asession = AsyncHTMLSession()
        request_coros = [self._get_webpage_response(url, asession) for url in self.urls]
        responses = await asyncio.gather(*request_coros)

        # render javascript
        render_coros = [self._render_webpage_response(response) for response in responses]
        htmls = await asyncio.gather(*render_coros)

        return htmls

    def _get_titles(self):
        """Parse the html for the title of the series

        Returns:
            str|None: The title of the axs event if it exists, else None
        """
        titles = []
        for html in self.htmls:
            title = html.find("h1.series-header__main-title", first=True)
            if title:
                title = title.full_text.strip()  # remove html tags and leading/trailing whitespace
            titles.append(title)

        return titles

    def run(self, filepath="", force=False):
        # TODO: actually process file
        print(self.titles)


class AxsGui:
    def __init__(self):
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

        self.file_img = Image.open("file.png")
        width, height = self.file_img.size
        self.file_img_resized = self.file_img.resize((width//7, height//7))
        self.file_img_tk = ImageTk.PhotoImage(self.file_img_resized)

        self.select_folder_button = tk.Button(self.filename_frame, image=self.file_img_tk, command=self._select_folder)
        # self.select_folder_button = tk.Button(self.filename_frame, image=self.file_img_tk, command=lambda: print("foo"))
        self.select_folder_button.pack(side=tk.RIGHT, ipadx=2, ipady=2)

        # RUN
        self.run_button = tk.Button(self.root, text="Run", command=lambda: self.scrape())
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
        start_time = time.time()                           # ----- Benchmark start ----- #

        scraper = AxsWebscraper(self.start_id, self.stop_id, self.outfile)
        scraper.run()
        print("\nFinished scrape")

        print(f"Time elapsed: {time.time() - start_time}") # ----- Benchmark stop ----- #

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
