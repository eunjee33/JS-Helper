import sys
from class3 import URLFinder

def main():
    # URL 입력받기
    if len(sys.argv) != 3 or sys.argv[1] != "-f":
        print("Usage: python test.py -f {js_file}")
        return
    
    js_file = sys.argv[2]
    
    # LinkFinderExecutor 실행
    URLFinder().find_url(js_file)

if __name__ == "__main__":
    main()
