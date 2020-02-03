from pathlib import Path
from re import findall
from json import dumps
from requests import get
from time import time, sleep
from datetime import datetime, timedelta
from bs4 import BeautifulSoup as BS
from fake_useragent import UserAgent

class Cralwer() :
    def __init__(self, *args, **kwargs) :
        self.period = kwargs["period"]
        self.folder = kwargs["folder"]
        self.sleep_time = kwargs["sleep"]

        self.url_id = {
            "정치" : 100, "경제" : 101, "사회" : 102, 
            "생활" : 103, "세계" : 104, "과학" : 105
        }
        self.url_id_eng = {
            "정치" : "politics", "경제" : "economy", "사회" : "society",
            "생활" : "living", "세계" : "world", "과학" : "science"
        }

        self.fake_headers = {"User-Agent" : UserAgent().chrome}
        self.start, self.end = self.get_date()

    def get_date(self) :
        l = findall(r'\d+', self.period)
        start = end = 0
        if len(l) != 2 :
            raise Exception("Error! Wrong period format : {}".format(self.period))

        if l[0] > l[1] :
            start = l[0]
            end = l[1]
        else :
            start = l[1]
            end = l[0]

        '''
            2004년 5월 1일 이전의 news를 크롤링 X
            오늘 랭킹 뉴스가 나오지 않았을 수도 있으므로 하루 전 news까지 크롤링
        '''
        start = datetime.strptime(
            min((datetime.today() - timedelta(days = 1)).strftime("%Y%m%d"), start), "%Y%m%d")
        end = datetime.strptime(max("20040501", end), "%Y%m%d")
        print("start : {} - end : {}".format(start, end))
        
        return start, end

    def create_folder(self) :
        if self.folder is None : # 현재 위치에 output을 저장
            self.folder = Path.cwd()
        else :
            self.folder = Path(self.folder).resolve()

        self.error_log = self.folder / "error.log"

        self.content_folder = self.folder / "news_contents"
        if not self.content_folder.exists() :
            self.content_folder.mkdir()

        # ./location/news_content/politics
        for category in self.url_id_eng.values() :
            category_folder = self.content_folder / category
            if not category_folder.exists():
                category_folder.mkdir()
                
        print("content_folder : {}".format(self.content_folder))

    def save_to_json(self, folder, date, data) :
        file_name = folder / "{}.json".format(date)
        with file_name.open("w", encoding = "utf-8") as fp :
            json_data = dumps(data, indent = 4, ensure_ascii = False)
            fp.write(json_data)

    def Sleep(self) :
        start = time()
        while (time() - start < self.sleep_time) :
            sleep(self.sleep_time - (time() - start))

    def extract_contents(self, category, links, ID, ext_tags) :
        contents = {}

        for idx, news_info in enumerate(links) :
            self.Sleep()
            contents[idx] = dict()

            title = news_info[0].strip()
            link = news_info[1].strip()
            contents[idx]['title'] = title
            contents[idx]['link'] = link
            contents[idx]['category'] = category

            news_res = get(link, headers = self.fake_headers)
            soup = BS(news_res.content, 'lxml')
            _ = [s.extract() for s in soup(ext_tags)]

            try :
                texts = soup.find(id = ID)
                article = texts.get_text().strip()
                contents[idx]['text'] = article
            except AttributeError :
                contents[idx]['text'] = "본문을 찾을 수 없습니다."

        return contents

    def start_crawling(self) :
        self.create_folder()
        
        news_url = "https://news.naver.com"
        ranking_url = "https://news.naver.com/main/ranking/popularDay.nhn?rankingType=popular_day&sectionId={}&date={}"

        date_links = {}
        for i in range(0, (self.start - self.end).days + 1) :
            date_str = (self.start - timedelta(days = i)).strftime("%Y%m%d")

            # 해당 날짜의 category 6개를 모두 저장
            temp_links = {key : ranking_url.format(str(value), date_str) for key, value in self.url_id.items()}

            date_links[date_str] = temp_links

        print("\nlen(date_links) : ", len(date_links), "\n")
        
        if not len(date_links) :
            raise Exception("Crawling할 기사가 없습니다.")

        try :
            for date, links in date_links.items() :
                for category, category_link in links.items() :
                    print("[ {} ] Crawling Date : [ {} ] Category : [ {} ]".format(
                        datetime.now().strftime("%Y/%m/%d %H:%M:%S"), date, category))
                    
                    category_res = get(category_link, headers = self.fake_headers)

                    soup = BS(category_res.content, 'lxml')

                    temp_links = soup.select(
                        '#wrap table td.content > div.content ol.ranking_list > li > div.ranking_text > div.ranking_headline > a'
                    )

                    temp_links = [[link.attrs['title'], news_url + link.attrs['href']] for link in temp_links]
                    # category_dic = {idx + 1 : link for idx, link in enumerate(temp_links)}

                    contents = self.extract_contents(category, temp_links, 'articleBodyContents', ['script', 'span', 'a', 'h4'])
                    self.save_to_json(self.content_folder / self.url_id_eng[category], date, contents)

        except KeyboardInterrupt :
            raise KeyboardInterrupt("KeyboardInterrupt Error")

        except Exception as e :
            with open(self.error_log, "a+", encoding = 'utf-8') as fp :
                str_ = (datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "\n" +
                    str(e) + "\n - - - - - - - - - - \n")
                fp.write(str_)

        print("\nFinished")