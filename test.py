import sys
from class3 import URLFinder
from class4 import URLRequester
import argparse

def main():
    """parser = argparse.ArgumentParser(description="Usage: python test.py -f {js_file}")
    parser.add_argument("-f", required=True, help="js_file")
    args = parser.parse_args()

    js_file = args.f
    
    # LinkFinderExecutor 실행
    url_finder = URLFinder()
    url_finder.run(js_file)"""
    
    url_requester = URLRequester()
    url_requester.run()


if __name__ == "__main__":
    main()
