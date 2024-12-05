import subprocess
import os

class URLFinder:
    def __init__(self, linkfinder_path="lib/linkfinder.py", temp_file="temp.txt", output_file="urls.txt"):
        self.linkfinder_path = linkfinder_path
        self.temp_file = temp_file
        self.output_file = output_file


    ## 최종 실행할 함수
    def find_url(self, js_file):
        result = self.execute_linkfinder(js_file)
        self.write_output(result)


    def execute_linkfinder(self, js_file):
        try:
            # subprocess를 사용해 linkfinder.py 실행
            command = ["python", self.linkfinder_path, "-i", js_file, "-o", "cli"]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            return result
        except subprocess.CalledProcessError as e:
            print(f"Error executing linkfinder.py: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def write_output(self, result):
        try:
            # temp.txt에 결과 저장
            with open(self.temp_file, "w") as temp:
                temp.write(result.stdout)
            
            # temp.txt 내용을 urls.txt에 이어 쓰기
            with open(self.temp_file, "r") as temp, open(self.output_file, "a") as output:
                output.write(temp.read())
            
            print(f"URLs successfully appended to {self.output_file}")
            
            # temp.txt 삭제
            if os.path.exists(self.temp_file):
                os.remove(self.temp_file)
            else:
                pass
        except Exception as e:
            print(f"Unexpected error: {e}")

