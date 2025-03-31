#!/usr/bin/env bash

# echo "$(realpath $0)"
required_path="$(dirname "$(dirname "$(realpath $0)")")"

if [ "$PWD" != "$required_path" ]; then
    echo ERROR: Script must be run from "$required_path" 1>&2
    exit 1
fi

if [ ! -d ./dist ]; then
    echo "ERROR: Project is not built yet. First run \`make build\`." 1>&2
    exit 1
fi

if [ -d ./package ]; then
    rm -rf ./package
fi
mkdir package

if [ "$(uname -o)" = "Msys" ]; then
    zip -r axs-webscraper_win_x86-64.zip dist/axs-webscraper.exe browser_drivers/;
    cp dist/axs-webscraper.exe axs-webscraper-core_win_x86-64.exe
    mv axs-webscraper_win_x86-64.zip axs-webscraper-core_win_x86-64.exe package
elif [ "$(uname -o)" = "Darwin" ]; then
    if [ "$(uname -m)" = "x86_64" ]; then
        tar czvf axs-webscraper_macos_x86-64.tar.gz dist/axs-webscraper dist/axs-webscraper.app browser_drivers/;
        cp dist/axs-webscraper axs-webscraper-core_macos_x86-64
        cp -a dist/axs-webscraper.app axs-webscraper-core_macos_x86-64.app
        mv axs-webscraper_macos_x86-64.tar.gz axs-webscraper-core_macos_x86-64 axs-webscraper-core_macos_x86-64.app package
    elif [ "$(uname -m)" = "arm64" ]; then
        tar czvf axs-webscraper_macos_arm64.tar.gz dist/axs-webscraper dist/axs-webscraper.app browser_drivers/;
        cp dist/axs-webscraper axs-webscraper-core_macos_arm64
        cp -a dist/axs-webscraper.app axs-webscraper-core_macos_arm64.app
        mv axs-webscraper_macos_arm64.tar.gz axs-webscraper-core_macos_arm64 axs-webscraper-core_macos_arm64.app package
    fi
fi
