import sys
from class3 import URLFinder
import argparse

def main():
    parser = argparse.ArgumentParser(description="Usage: python test.py -f {js_file}")
    parser.add_argument("-f", required=True, help="js_file")
    args = parser.parse_args()

    js_file = args.f
    
    # LinkFinderExecutor 실행
    URLFinder().find_url(js_file)

if __name__ == "__main__":
    main()
