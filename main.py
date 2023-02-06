from crawling import Crawling
from datetime import datetime
from hwp_to_pdf import hwp2pdf

import os
import argparse

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("--d", type=str, default=datetime.today().strftime("%Y%m%d"),
                      help="크롤링을 시작할 날짜, 디폴트는 오늘, 폴더명이기도 함")
    args.add_argument("--to_d", type=str, default="99999999",
                      help="마감일이 to_d포함 이전인 것만 크롤링 한다.")
    config = args.parse_args()

    d = config.d
    to_d = config.to_d
    params = {
        "main_url": "https://www.gojobs.go.kr/apmList.do?menuNo=401&mngrMenuYn=N&selMenuNo=400&upperMenuNo=&wd=1920", # 게시글 목록 url
        "post_url_first": "https://www.gojobs.go.kr/apmView.do", # 게시글 url 앞부분
        "down_url_first": "https://www.gojobs.go.kr/downFile.do", # 첨부파일 url 앞부분
    }

    # 크롤링할 폴더 지정
    folder = "crawling_data/"+d
    if not os.path.exists(folder):
        os.makedirs(folder)

    # 크롤링 시작
    crawler = Crawling(**params)
    crawler.crawling(d,to_d)

    # 게시글 데이터
    crawling_file_name = "게시글_"+d+".xlsx" # 게시글 데이터 엑셀파일
    crawler.save_crawling(os.path.join(folder,crawling_file_name))

    # 첨부파일 데이터
    down_folder = d # 첨부파일 저장할 폴더이름
    download_file_name = "첨부파일_"+d+".xlsx" # 첨부파일 내역 엑셀파일
    crawler.save_download(os.path.join(folder,down_folder), os.path.join(folder,download_file_name))

    # hwp파일을 pdf로
    # hwp2pdf(d)