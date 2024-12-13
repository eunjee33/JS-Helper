import argparse
import os
import requests
import shutil
from urllib.parse import urlparse
import subprocess
import json
from datetime import datetime

# Colors for output
RESET = "\033[0m"
BLUE = "\033[94m"
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BRIGHT_YELLOW = "\033[93;1m"

def get_timestamped_dir(base="Outputs"):
    """Generate a timestamped directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base, f"js_files_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def download_file(url, output_path):
    """Download a file from a URL."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.RequestException as e:
        raise FileNotFoundError(f"Failed to download: {url}. {e}")

def decode_js(input_file, output_file):
    """Run the webcrack decode process on a JavaScript file."""
    try:
        result = subprocess.run(
            ["webcrack", input_file],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(result.stdout)
            print(f"{GREEN}[+] Decoded and Saved:{RESET} {output_file}")
        else:
            raise Exception(f"Decoding failed for {input_file}")
    except FileNotFoundError:
        print(f"{RED}[!] Error:{RESET} webcrack tool not found. Please install webcrack.")
        raise

def process_json_file(json_file):
    """Process JavaScript files listed in a JSON file."""
    with open(json_file, "r") as f:
        data = json.load(f)

    timestamped_dir = get_timestamped_dir()
    failure_log = []

    for domain, js_types in data.items():
        print(f"\n{YELLOW}[Processing Domain]{RESET}: {CYAN}{domain}{RESET}")

        domain_dir = os.path.join(timestamped_dir, urlparse(domain).netloc.replace('.', '_'))
        origin_dir = os.path.join(domain_dir, "origin")
        decode_dir = os.path.join(domain_dir, "decode")
        os.makedirs(origin_dir, exist_ok=True)
        os.makedirs(decode_dir, exist_ok=True)

        for category, files in js_types.items():
            category_origin_dir = os.path.join(origin_dir, category)
            category_decode_dir = os.path.join(decode_dir, category)
            os.makedirs(category_origin_dir, exist_ok=True)
            os.makedirs(category_decode_dir, exist_ok=True)

            for js_file in files:
                parsed_url = urlparse(js_file)
                file_name = os.path.basename(parsed_url.path) or f"{domain.replace('.', '_')}_inline.js"
                origin_file = os.path.join(category_origin_dir, file_name)
                decoded_file = os.path.join(category_decode_dir, f"decoded_{file_name}")

                try:
                    if category in ["internal", "external"]:
                        download_file(js_file, origin_file)
                    elif category == "inline":
                        if os.path.exists(js_file):
                            shutil.copy(js_file, origin_file)
                        else:
                            raise FileNotFoundError(f"Inline file not found: {js_file}")

                    decode_js(origin_file, decoded_file)

                except FileNotFoundError as e:
                    failure_log.append(f"{js_file}: {e}")
                except Exception as e:
                    failure_log.append(f"{js_file}: {e}")

    if failure_log:
        failure_log_file = os.path.join(timestamped_dir, "failure_log.txt")
        with open(failure_log_file, "w", encoding="utf-8") as f:
            f.write("\n".join(failure_log))
        print(f"\n{RED}[!] Failed Files Logged to:{RESET} {failure_log_file}")

def process_single_js(js_file):
    """Process a single JavaScript file."""
    parsed_url = urlparse(js_file)
    base_name = os.path.basename(parsed_url.path) or "local_file"
    timestamped_dir = get_timestamped_dir()
    domain_dir = os.path.join(timestamped_dir, base_name)
    origin_dir = os.path.join(domain_dir, "origin")
    decode_dir = os.path.join(domain_dir, "decode")
    os.makedirs(origin_dir, exist_ok=True)
    os.makedirs(decode_dir, exist_ok=True)

    try:
        if parsed_url.scheme in ["http", "https"]:
            origin_file = os.path.join(origin_dir, base_name)
            decoded_file = os.path.join(decode_dir, f"decoded_{base_name}")
            download_file(js_file, origin_file)
        else:
            origin_file = os.path.join(origin_dir, os.path.basename(js_file))
            decoded_file = os.path.join(decode_dir, f"decoded_{os.path.basename(js_file)}")
            shutil.copy(js_file, origin_file)

        decode_js(origin_file, decoded_file)
    except Exception as e:
        print(f"{RED}[!] Error:{RESET} {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="M2. JavaScript Deobfuscator.")
    parser.add_argument("-json", help="js_files_20241210_121511.json")
    parser.add_argument("-url", help="https://www.example.com/js/app.js")
    parser.add_argument("-js", help="/path/to/local_file.js")
    args = parser.parse_args()

    if args.json:
        print(f"{BLUE}[Processing JSON File]{RESET}: {CYAN}{args.json}{RESET}")
        process_json_file(args.json)
    elif args.url:
        print(f"{BLUE}[Processing URL]{RESET}: {CYAN}{args.url}{RESET}")
        process_single_js(args.url)
    elif args.js:
        print(f"{BLUE}[Processing Local File]{RESET}: {CYAN}{args.js}{RESET}")
        process_single_js(args.js)
    else:
        print(f"{BRIGHT_YELLOW}Usage: python 2.py [-json JSON] [-url URL] [-js js]")
