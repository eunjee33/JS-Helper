import argparse
import os
import requests
import shutil
from urllib.parse import urlparse
import subprocess
import json
from datetime import datetime

from class1 import JavaScriptExtractor
import class2
from class3 import URLFinder
from class4 import URLRequester
from class5 import DataLeaker
from class6 import FunctionFinder


# Colors for output
RESET = "\033[0m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BRIGHT_YELLOW = "\033[93;1m"


if __name__ == "__main__":
    logging.getLogger("seleniumwire").setLevel(logging.ERROR)
    
    args = parser.parse_args()
    parser = argparse.ArgumentParser(description="JS-Helper")
    parser.add_argument("-u", "--url", help="Single url (e.g., https://example.com/)")
    parser.add_argument("-f", "--file", help="https://www.example.com/js/app.js or /path/to/local_file.js")
    parser.add_argument("-j", "--json", help="js_files_20241210_121511.json")
    
    javaScriptExtractor = JavaScriptExtractor()

    if args.url:
        print(f"{BLUE}[Processing URL]{RESET}: {CYAN}{args.url}{RESET}")
        javaScriptExtractor.process_single_js(args.url)
    else:
        print(f"{BRIGHT_YELLOW}Usage: python main.py --url URL [--json js_file.json] [--file js_file.js]")
