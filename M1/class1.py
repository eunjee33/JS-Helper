from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import httpx
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin, urlparse
from datetime import datetime
import logging, argparse
from colorama import Fore, Style, init
init(autoreset=True)  # 색상 자동 초기화


def is_internal(request_url, input_domain):
    """Check if a URL is internal based on the input domain."""
    parsed_input = urlparse(input_domain).netloc
    parsed_request = urlparse(request_url).netloc
    return parsed_input.split('.')[-2:] == parsed_request.split('.')[-2:]


class JavaScriptExtractor:
    """A class to extract JavaScript file paths using Selenium and HTTP/2 with httpx."""

    def __init__(self, domain, timeout=30):
        self.domain = domain
        self.timeout = timeout
        self.driver = None
        self.internal_js = set()
        self.external_js = set()
        self.inline_scripts = []

    def _setup_driver(self):
        """Setup Selenium Wire headless Chrome driver."""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-webgl")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36")
        seleniumwire_options = {"verify_ssl": False}
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options, seleniumwire_options=seleniumwire_options)

    def _extract_js_from_html(self, html):
        """Extract JavaScript files and inline scripts from HTML."""
        soup = BeautifulSoup(html, "html.parser")
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                full_url = urljoin(self.domain, src)
                if is_internal(full_url, self.domain):
                    self.internal_js.add(full_url)
                else:
                    self.external_js.add(full_url)
            elif script.string:
                self.inline_scripts.append(script.string.strip())
    
    def extract_with_selenium(self):
        """Extract JavaScript files using Selenium."""
        self._setup_driver()
        try:
            self.driver.get(self.domain)
            WebDriverWait(self.driver, 30).until(lambda d: d.execute_script("return document.readyState") == "complete")

            # Extract inline scripts
            self._extract_js_from_html(self.driver.page_source)

            # Extract network requests
            for request in self.driver.requests:
                if request.response and ".js" in request.path:
                    full_url = request.url
                    if is_internal(full_url, self.domain):
                        self.internal_js.add(full_url)
                    else:
                        self.external_js.add(full_url)
        except TimeoutException:
            print(f"[!] Timeout while waiting for {self.domain}")
        except WebDriverException as e:
            print(f"[!] WebDriver error: {e}")
        finally:
            self.driver.quit()

    def extract_with_httpx(self):
        """Extract JavaScript files using httpx for HTTP/2 requests."""
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36",
                "Referer": self.domain,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }

            with httpx.Client(http2=True, verify=False, timeout=self.timeout) as client:
                # 리다이렉션 비활성화
                response = client.get(self.domain, headers=headers, follow_redirects=False)

                # 403/302 상태 코드 처리
                if response.status_code in [302, 403]:
                    print(f"{Fore.RED}[!] Blocked Request - Status: {response.status_code}, URL: {self.domain}")
                    redirect_location = response.headers.get('Location')
                    if redirect_location:
                        print(f"{Fore.RED}[!] Redirected to: {redirect_location}")
                    return

                response.raise_for_status()  # 다른 HTTP 오류 발생 시 예외

                # Extract inline scripts
                self._extract_js_from_html(response.text)

        except httpx.RequestError as e:
            print(f"[!] HTTP/2 request failed for {self.domain}: {e}")


    def fetch_js_files(self):
        """Fetch all JavaScript file paths using both Selenium and HTTP/2."""
        try:
            print(f"{Fore.BLUE}[*] Extracting JavaScript files using Selenium for {self.domain}")
            self.extract_with_selenium()

            print(f"{Fore.BLUE}[*] Extracting JavaScript files using HTTP/2 for {self.domain}")
            self.extract_with_httpx()

            # Save inline scripts
            inline_script_files = save_inline_scripts(self.inline_scripts, self.domain)

            # 결과 병합
            combined_results = {
                "internal": list(self.internal_js),
                "external": list(self.external_js),
                "inline": inline_script_files,
            }

            return combined_results
        except Exception as e:
            # 에러 로그 출력
            print(f"{Fore.RED}[!] Error processing {self.domain}: {e}")
            return None

def print_summary(self):
    """Print the summary of extracted JS paths."""
    total_internal = len(self.internal_js)
    total_external = len(self.external_js)
    total_inline = len(self.inline_scripts)

    print(f"{Fore.GREEN}[+] Extracted JS paths:{Style.RESET_ALL}")
    print(f"  - Internal: {total_internal} files")
    print(f"  - External: {total_external} files")
    print(f"  - Inline: {total_inline} files")

def save_inline_scripts(inline_scripts, domain, output_dir="Outputs"):
    """Save inline JavaScript code to separate files and return their paths."""
    parsed_url = urlparse(domain)
    file_name = os.path.basename(parsed_url.path) or "index.html"
    domain_dir = os.path.join(output_dir, parsed_url.netloc)
    os.makedirs(domain_dir, exist_ok=True)

    saved_files = []
    for idx, script in enumerate(inline_scripts, start=1):
        file_path = os.path.abspath(os.path.join(domain_dir, f"{file_name}_{idx}.js"))
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(script)
            saved_files.append(file_path)
        except IOError as e:
            print(f"[!] Failed to save inline script {idx}: {e}")

    return saved_files

def save_results_to_file(results, output_dir, filename):
    """Save the extracted JavaScript file paths to a JSON file."""
    if not results or all(not v for v in results.values()):  # 모든 값이 비어있는 경우
        print(f"{Fore.YELLOW}[!] No results to save. Skipping file creation.")
        return

    try:
        os.makedirs(output_dir, exist_ok=True)
        file_path = os.path.abspath(os.path.join(output_dir, filename))
        with open(file_path, "w") as file:
            json.dump(results, file, indent=4)
        print(f"{Fore.GREEN}[+] Results saved to {file_path}")
    except IOError as e:
        print(f"{Fore.RED}[!] Error saving file: {e}")

if __name__ == "__main__":
    logging.getLogger("seleniumwire").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description="Extract JavaScript file paths using Selenium and HTTP/2 with httpx.")
    parser.add_argument("-d", "--domain", help="Single domain (e.g., https://example.com/)")
    parser.add_argument("-f", "--file", help="File containing a list of domains")
    parser.add_argument("-o", "--output", default="Outputs", help="Output directory for results")
    args = parser.parse_args()

    if not args.domain and not args.file:
        print(f"{Fore.YELLOW}Usage: python script.py -d <domain> or -f <file>")
    else:
        if args.domain:
            print(f"{Fore.BLUE}[*] Processing single domain: {args.domain}")
            extractor = JavaScriptExtractor(args.domain)
            js_files = extractor.fetch_js_files()

            if js_files and any(js_files.values()):  # 결과가 비어있지 않은 경우만 저장
                total_internal = len(js_files["internal"])
                total_external = len(js_files["external"])
                total_inline = len(js_files["inline"])

                print(f"{Fore.GREEN}[+] Extracted JS paths:{Style.RESET_ALL}")
                print(f"  - Internal: {total_internal} files")
                print(f"  - External: {total_external} files")
                print(f"  - Inline: {total_inline} files")

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"js_files_{timestamp}.json"
                save_results_to_file({args.domain: js_files}, args.output, output_file)
            else:
                print(f"{Fore.YELLOW}[!] No JavaScript files extracted for {args.domain}. Skipping file creation.")

        elif args.file:
            print(f"{Fore.BLUE}[*] Processing multiple domains from file: {args.file}")
            results = {}
            try:
                with open(args.file, "r") as file:
                    domains = file.read().splitlines()

                for idx, domain in enumerate(domains, start=1):
                    if domain.strip():
                        print(f"{Fore.YELLOW}[Processing Domain {idx}]: {Fore.CYAN}{domain}{Style.RESET_ALL}")
                        extractor = JavaScriptExtractor(domain)
                        js_files = extractor.fetch_js_files()

                        if js_files and any(js_files.values()):  # 결과가 비어있지 않은 경우만 추가
                            total_internal = len(js_files["internal"])
                            total_external = len(js_files["external"])
                            total_inline = len(js_files["inline"])

                            print(f"{Fore.GREEN}[+] Extracted JS paths:{Style.RESET_ALL}")
                            print(f"  - Internal: {total_internal} files")
                            print(f"  - External: {total_external} files")
                            print(f"  - Inline: {total_inline} files")

                            results[domain] = js_files
                        else:
                            print(f"{Fore.YELLOW}[!] No JavaScript files extracted for {domain}. Skipping.")

                if results:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    output_file = f"js_files_{timestamp}.json"
                    save_results_to_file(results, args.output, output_file)
                else:
                    print(f"{Fore.YELLOW}[!] No results to save for any domain.")

            except IOError as e:
                print(f"{Fore.RED}[!] Error reading file: {e}")