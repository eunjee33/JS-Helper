import subprocess
import os
import re
from urllib.parse import urljoin, urlparse


class URLFinder:
    def __init__(self, linkfinder_path="lib/linkfinder.py", urls_file="urls.txt", uniq_domains_file="uniq_domains.txt"):
        self.linkfinder_path = linkfinder_path
        #self.temp_file = "temp.txt"
        self.urls_file = urls_file
        self.uniq_domains_file = uniq_domains_file


    """전체 프로세스 실행"""
    def run(self, js_file):
        output = self.execute_linkfinder(js_file)
        urls = self.filter_links(output, js_file)
        uniq_domains = self.extract_domains(urls)
        self.write_output(urls, uniq_domains)


    """linkfinder tool 실행"""
    def execute_linkfinder(self, js_file):
        try:
            # subprocess를 사용해 linkfinder.py 실행
            command = ["python", self.linkfinder_path, "-i", js_file, "-o", "cli"]
            output = subprocess.run(command, capture_output=True, text=True, check=True)
            return output
        except subprocess.CalledProcessError as e:
            print(f"Error executing linkfinder.py: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


    """1. 추출한 URL filter - text/html 과 같은 html 타입 형태는 제거"""
    """2. 상대 경로 -> 절대 경로"""
    def filter_links(self, output, js_file):
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
        remove_pattern = re.compile("|".join(remove_types))

        urls = []

        for line in output.stdout.splitlines():
            line = line.strip()
            if remove_pattern.search(line):
                continue

            # 상대 경로 처리
            if line.startswith("/") and not line.startswith("//"):
                line = urljoin(base_url, line)
                urls.append(line)

            # 절대 경로 (`//`)와 HTTP/HTTPS 제외 (필터링 없이 추가)
            if line.startswith("//") or line.startswith("http://") or line.startswith("https://"):
                urls.append(line)
        
        return urls


    """unique domain 추출"""
    def extract_domains(self, urls):
        uniq_domains = set()

        for url in urls:
            parsed = urlparse(url)
            if parsed.netloc:  # 유효한 도메인인 경우만 처리
                uniq_domains.add(parsed.netloc)
        return uniq_domains


    """결과를 file(.txt)로 저장"""
    def write_output(self, urls, uniq_domains):
        try:
            with open(self.urls_file, "a") as f:
                for url in urls: 
                    f.write(url + "\n")

            print(f"URLs successfully appended to {self.urls_file}")

            with open(self.uniq_domains_file, "a") as f:
                for domain in uniq_domains:
                    f.write(domain + "\n")

            print(f"Domains successfully appended to {self.uniq_domains_file}")
        except Exception as e:
            print(f"Unexpected error: {e}")
