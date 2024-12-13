#!/bin/bash

set -e

# 색상 정의
RESET="\033[0m"
GREEN="\033[1;32m"
YELLOW="\033[1;33m"
BLUE="\033[1;34m"
RED="\033[1;31m"

echo -e "${BLUE}Step 1: Checking Python version...${RESET}"
python3 --version

echo -e "${BLUE}Step 2: Creating virtual environment...${RESET}"
python3 -m venv venv
chmod +x venv/bin/activate

echo -e "${BLUE}Step 3: Activating virtual environment...${RESET}"
source venv/bin/activate

echo -e "${BLUE}Step 4: Installing Python dependencies...${RESET}"
pip install --upgrade setuptools
pip install -r requirements.txt

echo -e "${BLUE}Step 5: Checking if Google Chrome is installed...${RESET}"
if ! command -v google-chrome > /dev/null; then
    echo -e "${YELLOW}Google Chrome is not installed. Downloading and installing...${RESET}"
    wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
    sudo dpkg -i google-chrome-stable_current_amd64.deb || sudo apt-get install -f -y
else
    echo -e "${GREEN}Google Chrome is already installed.${RESET}"
fi

echo -e "${BLUE}Step 6: Verifying Google Chrome installation...${RESET}"
google-chrome --version

echo -e "${GREEN}Setup complete!${RESET}"
echo -e "${YELLOW}\nTo proceed:${RESET}"
echo -e "${YELLOW}1. Activate the virtual environment:${RESET} ${GREEN}source venv/bin/activate${RESET}"
echo -e "${YELLOW}2. Run the script:${RESET} ${GREEN}python3 script.py${RESET}"

