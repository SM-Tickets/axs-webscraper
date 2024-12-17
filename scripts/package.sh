if [ "$(uname -o)" = "Msys" ]; then
    zip -r axs-webscraper_win_x86-64.zip axs-webscraper.exe browser_drivers/;
elif [ "$(uname -o)" = "Darwin" ]; then
    if [ "$(uname -m)" = "x86_64" ]; then
        tar czvf axs-webscraper_macos_x86-64.tar.gz axs-webscraper axs-webscraper.app browser_drivers/;
    elif [ "$(uname -m)" = "arm64" ]; then
        tar czvf axs-webscraper_macos_x86-64.tar.gz axs-webscraper axs-webscraper.app browser_drivers/;
    fi
fi
