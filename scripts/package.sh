#!/usr/bin/env bash

# echo "$(realpath $0)"
required_path="$(dirname "$(dirname "$(realpath $0)")")"

if [  "$PWD" != "$required_path" ]; then
    echo ERROR: Script must be run from "$required_path" 1>&2
    exit 1
fi

if [ -d ./package ]; then
    rm -rf ./package
fi
mkdir package

if [ "$(uname -o)" = "Msys" ]; then
    zip -r axs-webscraper_win_x86-64.zip axs-webscraper.exe browser_drivers/;
    cp axs-webscraper.exe axs-webscraper_win_x86-64.exe
    mv axs-webscraper_win_x86-64.zip axs-webscraper_win_x86-64.exe package
elif [ "$(uname -o)" = "Darwin" ]; then
    if [ "$(uname -m)" = "x86_64" ]; then
        tar czvf axs-webscraper_macos_x86-64.tar.gz axs-webscraper axs-webscraper.app browser_drivers/;
        cp axs-webscraper axs-webscraper_macos_x86-64
        cp -a axs-webscraper.app axs-webscraper_macos_x86-64.app
        mv axs-webscraper_macos_x86-64.tar.gz axs-webscraper_macos_x86-64 axs-webscraper_macos_x86-64.app package
    elif [ "$(uname -m)" = "arm64" ]; then
        tar czvf axs-webscraper_macos_arm64.tar.gz axs-webscraper axs-webscraper.app browser_drivers/;
        cp axs-webscraper axs-webscraper_macos_arm64
        cp -a axs-webscraper.app axs-webscraper_macos_arm64.app
        mv axs-webscraper_macos_arm64.tar.gz axs-webscraper_macos_arm64 axs-webscraper_macos_arm64.app package
    fi
fi
