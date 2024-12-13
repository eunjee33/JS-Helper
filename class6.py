import esprima
import json
import os
import ssl
from gzip import GzipFile
from colorama import Fore, Style, init
import argparse

try:
    from StringIO import StringIO
    readBytesCustom = StringIO
except ImportError:
    from io import BytesIO
    readBytesCustom = BytesIO

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

init(autoreset=True)


class FunctionFinder:
    def __init__(self, input_file="test.js", output_file="functions.json"):
        self.input_file = input_file
        self.output_file = output_file
        self.urls = []
        self.found_functions = []

        self.keywords = {
            "file": ["file", "upload", "download"],
            "escape": ["escape", "sanitize"],
            "auth": ["auth", "permission", "login", "role"],
            "crypto": ["encrypt", "decrypt", "encode", "decode", "aes", "sha"]
        }


    """전체 프로세스 실행"""
    def run(self, js_file):
        self.input_file = js_file
        js_code = self.read_js_file()
        self.find_function_in_file(js_code)
        
        if not self.found_functions:
            print(f"{Fore.YELLOW} - Can't Find any Funtions in {self.input_file}")
        else:
            self.save_to_json(self.found_functions, output_file=self.output_file)


    """input이 URL일 수도, local file 일 수도 있으니 형식을 맞춰주기 - linkfinder 참고"""
    def read_js_file(self):
        # URL일 경우
        if self.input_file.startswith(('http://', 'https://',
                            'file://', 'ftp://', 'ftps://')):
            return self.send_request(self.input_file)

        # Local file일 경우
        local_file = os.path.abspath(self.input_file)
        if os.path.exists(local_file):
            with open(local_file, "r", encoding="utf-8") as f:
                return f.read()
        else :
            print(f"{Fore.RED}[!] Don't exist {local_file}")
    

    """js 파일 읽기 - linkfinder 참고"""
    def send_request(sel, url):
        q = Request(url)

        q.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36')
        q.add_header('Accept', 'text/html,\
            application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        q.add_header('Accept-Language', 'en-US,en;q=0.8')
        q.add_header('Accept-Encoding', 'gzip')

        try:
            sslcontext = ssl.create_default_context()
            response = urlopen(q, context=sslcontext)
        except:
            sslcontext = ssl.create_default_context()
            response = urlopen(q, context=sslcontext)

        if response.info().get('Content-Encoding') == 'gzip':
            data = GzipFile(fileobj=readBytesCustom(response.read())).read()
        elif response.info().get('Content-Encoding') == 'deflate':
            data = response.read().read()
        else:
            data = response.read()

        return data.decode('utf-8', 'replace')
        

    """함수 이름에 맞는 타입을 반환"""
    def get_function_type(self, function_name):
        for func_type, keywords in self.keywords.items():
            if any(keyword in function_name.lower() for keyword in keywords):
                return func_type
        return None


    """JavaScript 코드에서 특정 함수 이름 찾기"""
    def find_function_in_file(self, js_code):
        try:
            # JavaScript 코드를 AST로 변환
            ast = esprima.parseScript(js_code, tolerant=True, loc=True)
        except Exception as e:
            print(f"Error parsing {self.input_file}: {e}")
            return []

        print(f"{Fore.BLUE}[*] Find Functions for {self.input_file}")
        # AST 탐색 시작
        for node in ast.body:
            self.traverse_node(node)

        return self.found_functions


    """AST에서 함수 선언 및 표현식 찾기"""
    def traverse_node(self, node):
        # 함수 선언 처리: function fileDownload() { ... }
        if isinstance(node, esprima.nodes.FunctionDeclaration):
            func_type = self.get_function_type(node.id.name)
            # 키워드에 매칭되는 함수만 저장
            if func_type:  
                func_info = {
                    "type": func_type,
                    "name": node.id.name,
                    "file": self.input_file,
                    "line": node.loc.start.line,
                }
                self.found_functions.append(func_info)
                print(f" * Found {Fore.CYAN}{func_type}{Style.RESET_ALL} Function {Fore.CYAN}{func_info['name']}{Style.RESET_ALL}"
                      f"in {Fore.CYAN}{func_info['file']}{Style.RESET_ALL} at line {Fore.CYAN}{func_info['line']}{Style.RESET_ALL}")
                
        # 변수 선언에서 함수 표현식 처리: const fileDownload = function() { ... }
        if isinstance(node, esprima.nodes.VariableDeclarator):
            func_type = self.get_function_type(node.id.name)
            # 키워드에 매칭되는 함수만 저장
            if func_type:  
                func_info = {
                    "type": func_type,
                    "name": node.id.name,
                    "file": self.input_file,
                    "line": node.loc.start.line,
                }
                self.found_functions.append(func_info)
                print(f" * Found {Fore.CYAN}{func_type}{Style.RESET_ALL} Function {Fore.CYAN}{func_info['name']}{Style.RESET_ALL} "
                      f"in {Fore.CYAN}{func_info['file']}{Style.RESET_ALL} at line {Fore.CYAN}{func_info['line']}{Style.RESET_ALL}")

        # 객체 메서드 처리: const obj = { fileDownload() { ... } }
        if isinstance(node, esprima.nodes.Property) and isinstance(node.value, (esprima.nodes.FunctionExpression, esprima.nodes.ArrowFunctionExpression)):
            func_type = self.get_function_type(node.key.name)
            # 키워드에 매칭되는 함수만 저장
            if func_type:  
                func_info = {
                    "type": func_type,
                    "name": node.key.name,
                    "file": self.input_file,
                    "line": node.loc.start.line,
                }
                self.found_functions.append(func_info)
                print(f" * Found {Fore.CYAN}{func_type}{Style.RESET_ALL} Function {Fore.CYAN}{func_info['name']}{Style.RESET_ALL} "
                      f"in {Fore.CYAN}{func_info['file']}{Style.RESET_ALL} at line {Fore.CYAN}{func_info['line']}{Style.RESET_ALL}")

        # 자식 노드 탐색
        for attr in ['body', 'declarations', 'properties']:
            if hasattr(node, attr):
                children = getattr(node, attr, [])
                if isinstance(children, list):
                    for child in children:
                        self.traverse_node(child)


    """결과를 JSON 파일로 저장"""
    def save_to_json(self, results, output_file="test.json"):  
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
            print(f"{Fore.GREEN}[*] Successfully appended to {output_file}")
        except Exception as e:
            print(f"{Fore.RED}[!] Unexpected error: {e}")


if __name__ == "__main__":    
    parser = argparse.ArgumentParser(description="Extract Important Functions from Javascript file")
    parser.add_argument("-f", "--file", help="js_file")
    args = parser.parse_args()

    if not args.file:
        print(f"{Fore.YELLOW}Usage: python script.py -f <file>")
        
    else:
        js_file = args.file
        
        functionFinder = FunctionFinder()
        functionFinder.run(js_file)