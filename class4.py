import requests
import json
from colorama import Fore, Style, init
import sys
import ast
import argparse

init(autoreset=True)


class URLRequester:
    def __init__(self, headers=None, cookies=None, input_file="urls.txt", output_file="results.json"):
        self.headers = headers
        self.cookies = cookies
        self.input_file = input_file
        self.output_file = output_file
        self.urls = []


    """전체 프로세스 실행"""
    def run(self):        
        self.load_urls()
        results = self.fetch_data()

        self.save_to_json(results, output_file=self.output_file)


    """input_file에서 url 읽어오기"""
    def load_urls(self):
        try:
            with open(self.input_file, 'r') as f:
                self.urls = list(set(line.strip() for line in f if line.strip()))
            print(f"{Fore.GREEN}[*] {len(self.urls)}개의 URL을 읽어들였습니다.")
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Can't find {self.input_file}")
        except Exception as e:
            print(f"{Fore.RED}[!] URL 로드 중 오류 발생: {e}")


    """URL에 request 보내기"""
    def fetch_data(self):
        results = []
        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  # HTTP 에러가 있는지 체크

                try:
                    response_body = response.json()  # JSON 파싱 시도
                except requests.exceptions.JSONDecodeError:
                    response_body = response.text

                # 헤더가 있는 경우 헤더 포함하여 요청
                if self.headers or self.cookies:
                    with_cookies_response = requests.get(url, headers=self.headers, cookies=self.cookies)
                    try:
                        with_headers_response_body = with_cookies_response.json()  # JSON 파싱 시도
                    except requests.exceptions.JSONDecodeError:
                        with_cookies_response.text  # JSON이 아니면 raw 텍스트로 저장

                    diff = False if response_body == with_headers_response_body else True
                
                if self.cookies:
                    results.append({"url": url, "status": response.status_code, "response_header": dict(response.headers), "Content-Length": len(response_body), "diff": diff})
                else:
                    results.append({"url": url, "status": response.status_code, "response_header": dict(response.headers), "Content-Length": len(response_body)})
        
                print(f" - {url} {Fore.CYAN}(성공){Style.RESET_ALL}")
            except requests.exceptions.RequestException as e:
                results.append({"url": url, "status": "error", "error": str(e)})
                print(f" - {url} (실패: {Fore.YELLOW}{e}){Style.RESET_ALL}")
        return results
    

    """결과를 JSON 파일로 저장"""
    def save_to_json(self, results, output_file="test.json"):  
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"{Fore.GREEN}[*] 결과가 {output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"{Fore.RED}[!] 결과 저장 중 오류 발생: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Requests endpoint from urls.txt")
    parser.add_argument("-H", "--headers", help="Headers", default="")
    parser.add_argument("-C", "--cookies", help="Cookies", default="")
    args = parser.parse_args()

    headers = args.headers
    cookies = args.cookies

    if headers:
        cookies = ast.literal_eval(cookies)
    if cookies:
        cookies = ast.literal_eval(cookies)

    url_requester = URLRequester(headers=headers, cookies=cookies)
    url_requester.run()

