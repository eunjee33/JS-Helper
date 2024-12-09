import requests
import json


class URLRequester:
    def __init__(self, input_file="urls.txt", output_file="results.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.urls = []


    """전체 프로세스 실행"""
    def run(self):        
        self.load_urls()
        results = self.fetch_data()
        self.save_results(results)


    """input_file에서 url 읽어오기"""
    def load_urls(self):
        try:
            with open(self.input_file, 'r') as f:
                self.urls = [line.strip() for line in f if line.strip()]
            print(f"{len(self.urls)}개의 URL을 읽어들였습니다.")
        except FileNotFoundError:
            print("파일을 찾을 수 없습니다. 경로를 확인하세요.")
        except Exception as e:
            print(f"URL 로드 중 오류 발생: {e}")


    """URL에 request 요청 보내기"""
    def fetch_data(self):
        results = []
        for url in self.urls:
            try:
                response = requests.get(url)
                response.raise_for_status()  # HTTP 에러가 있는지 체크
                results.append({"url": url, "status": response.status_code, "data": response.json()})
                print(f"{url} - 성공")
            except requests.exceptions.RequestException as e:
                results.append({"url": url, "status": "error", "error": str(e)})
                print(f"{url} - 실패: {e}")
        return results


    """결과를 JSON 파일로 저장"""
    def save_results(self, results):  
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"결과가 {self.output_file}에 저장되었습니다.")
        except Exception as e:
            print(f"결과 저장 중 오류 발생: {e}")

