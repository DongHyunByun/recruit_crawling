import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
import pandas as pd
from urllib import request,parse
import os
import sys

class Crawling:
    # url call 함수 파라미터명
    post_keys = ["jobsecode", "empmnsn"]  # 게시글
    down_keys = ["filenm","uuid","saveGbn"]  # 첨부파일

    cols = ["공고명", "기관명", "채용직급", "근무지역", "장애인 채용 / 우대", "등록일", "마감일", "첨부파일", "관련링크", "본문"]

    crawling_list = []
    crawling_list_down = []

    from_date_str = datetime.today().strftime("%Y%m%d")
    to_date_str = "99999999"

    def __init__(self,main_url,post_url_first,down_url_first):
        self.main_url = main_url
        self.post_url_first = post_url_first
        self.down_url_first = down_url_first

    def crawling(self,from_date_str=from_date_str, to_date_str=to_date_str):
        '''
        :param from_date_str: 시작할 날짜
        :return:
        '''
        self.from_date_str = from_date_str
        self.to_date_str = to_date_str

        page_number=1
        while(1):
            # 목록 페이지 get
            now_page_url = self.main_url+"&pageIndex="+str(page_number)
            page = self.try_request(now_page_url)  # get요청 후 응답 수신
            soup = bs(page.text, "html.parser")

            # 끝페이지이면 종료
            if soup.find("td", {"class": "emptyRow"}):
                print("###########end############")
                break

            # 게시글 하나씩 크롤링
            posts = soup.find_all('td', {"class": "ta_l elip"})
            for pst in posts:
                # 게시글 url get
                post_values = self.get_value(pst.a["href"])

                if not post_values:
                    continue

                post_url = self.get_url(self.post_url_first,self.post_keys,post_values)

                row = {
                    "식별 코드" : "70_"+post_values[-1],
                    "시군구_년월일" : "",
                    "담당부서명" : "",
                    "담당자명" : "",
                    "담당자 전화 번호" : "",
                    "관련 근거 명" : "",
                    "등록 일자" : "",
                    "서비스 명" : "",
                    "서비스 내용" : "",
                    "복지_URL" : post_url,
                    "구분" : "채용",
                    "키워드" : "",
                    "입력일자" : "",
                    "등록여부" : "N",
                    "마감일":"",
                    "근무지역":"",
                }

                row_down = {
                    "식별 코드" : "70_"+post_values[-1],
                    "SEQ" : "",
                    "제공처" : "나라장터",
                    "고유번호" : post_values[-1],
                    "복지_URL" : post_url,
                    "첨부_URL" : "",
                    "확장자" : "",
                    "경로" : ""
                }
                row_down_list = []

                # 게시글 페이지 get
                post_page = self.try_request(post_url)
                post_soup = bs(post_page.text, "html.parser")
                info_list = post_soup.find("table",{"id":"apmViewTbl"}).findChildren("tr",recursive=False)

                # 게시물 크롤링
                for info in info_list:
                    if info.th:
                        title = info.th.text
                    else :
                        title = "본문"

                    if title not in self.cols:
                        continue

                    if self.get_info(row,row_down,row_down_list,title,info):
                        return

                # 경기도, 마감일이 to_date_str이전인 것만
                if (("경기" in row["담당부서명"]) or ("경기" in row["근무지역"])) and (row["마감일"]<=to_date_str) :
                    print(row)
                    self.crawling_list.append(row)
                    print(row_down_list)
                    self.crawling_list_down.extend(row_down_list)

            page_number+=1
            # break

    def get_value(self,href):
        '''
        게시글의 url을 가져오기위해 필요한 value를 반환한다
        '''
        try:
            start_index = href.index("(")

            L = href[start_index + 1:-1].split("',")
            size = len(L)
            for i in range(size):
                if i==size-1:
                    L[i]=L[i].strip()[1:-1]
                else:
                    L[i]=L[i].strip()[1:]

            return L
        except:
            return

    def get_url(self,url_first,url_keys,url_values):
        '''
        :param url_first: url앞부분
        :param url_keys: url호출 함수의 키
        :param href: url호출 함수의 value가 있는 href

        :return: url
        '''

        # 게시글 url get
        pk_size = len(url_keys)
        assert len(url_values)==pk_size

        url_last = ""
        for i in range(pk_size):
            if i == pk_size - 1:
                url_last += url_keys[i] + "=" + parse.quote(url_values[i])
            else:
                url_last += url_keys[i] + "=" + parse.quote(url_values[i]) + "&"

        url = url_first + "?" + url_last

        return url

    def replace_text(self,text,remove_text=["\r","\n","\t","\xa0"]):
        '''
        text에 필요없는 remove_text를 제거한다
        '''
        text = text.strip()
        for r in remove_text:
            text = text.replace(r,"")
        return text

    def get_info(self,row,row_down,row_down_list,t,elmt):
        '''
        게시글의 html에서 필요한 텍스트를 추출한다.
        종료조건을 만족하면 True를 리턴한다.
        '''
        if t== "공고명":
            row["서비스 명"] = self.replace_text(elmt.td.text)
        elif t== "기관명":
            row["담당부서명"] = self.replace_text(elmt.td.text)
        elif t=="본문":
            row["서비스 내용"] = self.replace_text(elmt.textarea.text)[:2000]
        elif t=="근무지역":
            row["근무지역"] = self.replace_text(elmt.td.text)
        elif t=="등록일": # 등록일,마감일
            from_d,to_d = (elmt.find_all("td")[0].text, elmt.find_all("td")[1].text)

            from_d_str = "".join(from_d.split("-"))
            to_d_str = "".join(to_d.split("-")) #마감일자

            if from_d_str < self.from_date_str:  # from_date 이전에 등록된 게시물이 있으면 종료
                return True
            else:
                row["시군구_년월일"] = "99_"+from_d_str
                row["등록 일자"] = from_d_str
                row["마감일"] = to_d_str

        elif t=="첨부파일":
            down_list = elmt.find_all('a')
            size = len(down_list)

            for i in range(size):
                row_down_temp = dict(row_down)

                href = elmt.find_all("a")[i]["href"]
                down_values = self.get_value(href)
                if not down_values:
                    continue

                file_name = down_values[0]
                url = self.get_url(self.down_url_first, self.down_keys, down_values)

                row_down_temp["SEQ"] = row_down_temp["식별 코드"]+"_"+str(i+1)
                row_down_temp["파일명"] = file_name
                row_down_temp["첨부_URL"] = url
                row_down_temp["확장자"] = file_name[-3:]
                row_down_temp["경로"] = "FILE서버 기준경로\기준일자\\"+row_down_temp["SEQ"]

                row_down_list.append(row_down_temp)

    def try_request(self,url):
        '''
        request를 수행한다. 실패시 30초 대기 후 다시 시도한다. 총 3회 시도한다
        '''
        for i in range(3):
            try:
                post_page = requests.get(url)
                return post_page
            except:
                print("except!")
                if i == 2:
                    sys.exit("3회 시도 실패로 강제종료")
                time.sleep(30)

    def save_crawling(self,path):
        '''
        crawling함수 작동 후 crawling_list에 있는 데이터를 csv파일에 저장한다.
        '''

        xlsx_cols = ["식별 코드", "시군구_년월일", "담당부서명", "담당자명", "담당자 전화 번호", "관련 근거 명", "등록 일자", "서비스 명", "서비스 내용", "복지_URL",
                     "구분", "키워드1", "입력일자", "등록여부"]

        total_dict = {col:[] for col in xlsx_cols}
        for post_dict in self.crawling_list:
            for col in xlsx_cols:
                total_dict[col].append(post_dict.get(col,None))

        df = pd.DataFrame(total_dict)
        df.to_excel(path, index=False)

    def save_download(self,down_folder,down_path):
        '''
        crawling함수 작동 후 carling_list에 있는 정보를 이용하여 첨부파일을 저장한다
        '''

        xlsx_down_cols = ["식별 코드", "SEQ", "제공처", "고유번호", "파일명", "복지_URL", "첨부_URL", "확장자", "경로"]

        if not os.path.exists(down_folder):
            os.makedirs(down_folder)

        total_dict = {col:[] for col in xlsx_down_cols}
        for down_dict in self.crawling_list_down:
            for col in xlsx_down_cols:
                total_dict[col].append(down_dict.get(col, None))

                if col=="첨부_URL":
                    request.urlretrieve(down_dict[col], down_folder+"/"+down_dict["SEQ"]+"."+down_dict["파일명"].split(".")[-1])

        df = pd.DataFrame(total_dict)
        df.to_excel(down_path,index=False)