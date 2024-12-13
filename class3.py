import subprocess
import re
import os
import html
from urllib.parse import urljoin, urlparse
from colorama import Fore, init
import argparse
import os
from collections import OrderedDict


init(autoreset=True)


class URLFinder:
    def __init__(self, linkfinder_path="lib/linkfinder.py", urls_file="urls.txt", files_file="files.txt", uniq_domains_file="uniq_domains.txt"):
        self.linkfinder_path = linkfinder_path
        self.urls_file = urls_file
        self.files_file = files_file
        self.uniq_domains_file = uniq_domains_file


    """전체 프로세스 실행"""
    def run(self, js_file):
        output = self.execute_linkfinder(js_file)
        urls, files = self.filter_links(output, js_file)
        links = urls + files
        uniq_domains = self.extract_domains(links)

        self.save_to_txt(urls, output_file=self.urls_file)
        self.save_to_txt(files, output_file=self.files_file)
        self.save_to_txt(uniq_domains, output_file=self.uniq_domains_file)


    """linkfinder tool 실행"""
    def execute_linkfinder(self, js_file):
        try:
            # subprocess를 사용해 linkfinder.py 실행
            command = ["python", self.linkfinder_path, "-i", js_file, "-o", "cli"]
            output = subprocess.run(command, capture_output=True, text=True, check=True)
            return output
        except subprocess.CalledProcessError as e:
            print(f"{Fore.RED}[!] Error executing linkfinder.py: {e}")
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}")


    """1. 추출한 URL filter - text/html 과 같은 html 타입 형태는 제거"""
    """2. 상대 경로 -> 절대 경로"""
    def filter_links(self, output, js_file):
        base_url = ""
        if js_file.rsplit('/', 1)[0]:
            base_url = js_file.rsplit('/', 1)[0] + '/'

        remove_types = [
            r'text/.*',         # 모든 텍스트 타입
            r'image/.*',        # 모든 이미지 타입
            r'video/.*',        # 모든 비디오 타입
            r'audio/.*',        # 모든 오디오 타입
            r'application/.*',  # 모든 애플리케이션 타입
            r'font/.*',         # 모든 폰트 타입
            r'multipart/.*',    # 모든 멀티파트 타입
            r'message/.*'       # 모든 메시지 타입
        ]
        remove_space_pattern = r'\s'  # 띄어쓰기가 있는 경우
        remove_pattern = re.compile("|".join(remove_types) + "|" + remove_space_pattern)

        urls = []
        files = []

        for line in output.stdout.splitlines():
            line = line.strip()

            if line.startswith("//"):
                line += "https:"

            # 상대 경로 처리
            if line.startswith("/"):
                line = urljoin(base_url, line)

            line = self.clean_url(line)
            if remove_pattern.search(line):
                continue

            if self.categorize_url(line) == "file":
                files.append(line)
            else:
                urls.append(line)

        return urls, files


    def categorize_url(self, url):
        _, ext = os.path.splitext(url)
        if ext:
            return "file"
        else:
            return "url"


    """URL에서 경로만 가져오는 함수"""
    def clean_url(self, url):
        url = html.unescape(url)
        url = url.split('?')[0].split('#')[0]
        return url


    """unique domain 추출"""
    def extract_domains(self, urls):
        uniq_domains = set()

        for url in urls:
            parsed_url = urlparse(url)
            if parsed_url.hostname:  # hostname이 존재할 경우만 추가
                    uniq_domains.add(parsed_url.hostname)

        return uniq_domains


    """결과를 file(.txt)로 저장"""
    def save_to_txt(self, results, output_file="test.txt"):
        try:
            with open(output_file, "a") as f:
                for result in results:
                    f.write(result + "\n")
            print(f"{Fore.GREEN}[*] Successfully appended to {output_file}")

        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}")


def remove_duplicates_from_file(file_path):
    try:
        # 파일 열기
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 중복 제거 (set을 사용하여 중복된 줄을 제거)
        unique_lines = set(lines)

        # 중복 제거된 URL을 다시 파일에 씁니다
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(unique_lines)

    except Exception as e:
        print(f"파일 처리 중 오류 발생: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Urls from JavaScript file using linkfinder")
    parser.add_argument("-f", "--file", help="js_file - url or local file")
    parser.add_argument("-d", "--directory", help="directory javascripts is stored")
    args = parser.parse_args()
    
    if not args.file and not args.directory:
        print(f"{Fore.YELLOW}Usage: python script.py -d <directory> or -f <file>")
        
    else:
        url_finder = URLFinder()

        if args.file:
            js_file = args.file
            url_finder.run(js_file)
        
        elif args.directory:
            js_folder = args.directory

            for root, dirs, files in os.walk(js_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    url_finder.run(file_path)

            remove_duplicates_from_file("urls.txt")
            remove_duplicates_from_file("files.txt")
            remove_duplicates_from_file("uniq_domains.txt")
            