import sys
from re import findall
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import (NoSuchElementException, TimeoutException, 
    StaleElementReferenceException)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from argparse_type_check import bool_spelling_check, level_spelling_check
from Utils import Sleep, korea_time, save_json_data, get_pages
from Log import Logger
from Save import Saver

class Crawler() :
    def __init__(self, **kwargs) :
        current_time  = self.create_folder(kwargs["folder"])
        
        if all(value is None for value in [kwargs["words"], kwargs["file"]]) :
            self.logger.NoInputsError(sys._getframe().f_lineno)
            
        if kwargs["file"] is not None : # 우선 순위 : kwrags["file"] > kwargs["words"]
            self.words_dic = self.dic_from_file(Path(kwargs["file"]).resolve())
        else :
            self.words_dic = self.dic_from_arguments(**kwargs)

        # 모든 words에 적용되는 공통 옵션
        self.browser_type = kwargs["browser"].lower() if kwargs["browser"].lower() in ["chrome", "firefox"] else "firefox"
        self.headless_mode = kwargs["headless"]
        self.sleep_time = kwargs["sleep"]
        self.patience_time = max(kwargs["patience"], 1) # 적어도 1초는 기다림
        self.levels_dic = {"초급" : 1, "중급" : 2, "고급" : 3} # 0은 "전체"라 필요없음

        save_json_data(self.logs_folder / "crawlingList - {}.json".format(current_time), self.words_dic) # 크롤링 목록 저장
          
        # 차례대로 page, word, level(1 : 초급, 2 : 중급, 3 : 고급)
        self.query = ("https://en.dict.naver.com/#/search?range=example&" +
            "page={}&query={}&shouldSearchVlive=false&exampleLevel=exist:{}")
        self.current_page_number = "#searchPage_example_paginate strong" # 현재 page는 진하게 표시되어 있음
        self.examples_area = "#searchPage_example .component_example .row" # 한글, 영어 예문이 저장된 곳
        
        self.logger.Arguments(**kwargs)
        self.saver = Saver(self.words_folder, self.logger, kwargs["csv_file"], kwargs["db_file"])

    def create_folder(self, folder_location) :
        # 현재 위치에 결과 저장
        self.folder = Path.cwd() if folder_location is None else Path(folder_location).resolve()
        if not self.folder.exists() :
            self.logger.FileNotExistsError(sys._getframe().f_lineno, self.folder)
        
        result_folder = self.folder / "Results"
        self.words_folder = result_folder / "words"
        self.logs_folder = result_folder / "logs"
        for folder in [result_folder, self.words_folder, self.logs_folder] :
            if not folder.exists() :
                folder.mkdir()

        current_time = korea_time("%Y%m%d_%H%M%S")
        log_file = self.logs_folder / "logs - {}.txt".format(current_time)
        self.logger = Logger("Model.py", log_file)

        return current_time
        
    def dic_from_arguments(self, **kwargs) :
        words_dic = dict()

        if kwargs["levels"] is None :
            levels = ["초급", "중급", "고급"]
        else :
            levels = [level for level in kwargs["levels"]]        
        levels.sort(reverse = True) # 초급, 중급, 고급 순으로 크롤링
        length = len(levels)

        start_page, end_page = get_pages(kwargs["pages"], self.logger)

        for word in kwargs["words"] :
            if word not in words_dic :
                words_dic[word] = {
                    "levels" : levels, "start_page" : [start_page, ] * length, "end_page" : [end_page, ] * length,
                    "user" : [kwargs["user"], ] * length, "trsl" : [kwargs["translator"], ] * length
                }

        return words_dic

    def dic_from_file(self, input_file) :
        if not input_file.exists() :
            self.logger.FileNotExistsError(sys._getframe().f_lineno, input_file)
            
        with input_file.open("r", encoding = "utf-8") as fp :
            # 주석문과 공백 라인 제외
            lines = [line.strip() for line in fp.readlines() 
                     if ((not line.strip().startswith('#')) and (line.strip() != ''))]
            
        words_dic = dict()
        for line in lines :
            sets = [subline.strip() for subline in line.split('/')]
            if len(sets) <= 1 :
                self.logger.InvalidLineError(sys._getframe().f_lineno, line)
                
            # word만 따로 추출
            word = sets[0]
            sets = sets[1 : ]
            
            if word not in words_dic :
                words_dic[word] = {
                    "levels" : [], "start_page" : [], "end_page" : [], "user" : [], "trsl" : []
                }

                for set_ in sets :
                    # 옵션은 최대 3개까지 저장
                    if len(words_dic[word]["levels"]) == 3 :
                        break
                        
                    tokens = [token.strip() for token in set_.split(' ')]
                    if len(tokens) != 4 : # level page user trsl
                        self.logger.InvalidSetError(sys._getframe().f_lineno, word, set_)
                        
                    # 중복된 표현 수준의 설정이 있을 경우, 먼저 입력된 설정만 사용
                    if tokens[0] in words_dic[word]["levels"] :
                        continue
                    
                    try :
                        words_dic[word]["levels"].append(level_spelling_check(tokens[0]))
                    except Exception :
                        self.logger.InvalidSetError(sys._getframe().f_lineno, word, set_)

                    start_page, end_page = get_pages([int(n) for n in tokens[1].split("-")], self.logger)
                    words_dic[word]["start_page"].append(start_page)
                    words_dic[word]["end_page"].append(end_page)

                    try :
                        words_dic[word]["user"].append(bool_spelling_check(tokens[2]))
                        words_dic[word]["trsl"].append(bool_spelling_check(tokens[3]))
                    except Exception :
                        self.logger.InvalidSetError(sys._getframe().f_lineno, word, set_)
                        
        return words_dic

    def get_one_example(self, driver, idx) :
        return driver.find_elements_by_css_selector(self.examples_area)[idx]
    
    def get_eng_area(self, driver, idx) :
        while True :
            try :
                text = self.get_one_example(driver, idx).find_elements_by_css_selector("p")[0].text.strip()
                return text
            except (NoSuchElementException, StaleElementReferenceException) as e :
                Sleep(0.2)
        
    def get_kor_area(self, driver, idx) :
        while True :
            try :
                text = self.get_one_example(driver, idx).find_elements_by_css_selector("p")[1].text.strip()
                return text
            except StaleElementReferenceException :
                Sleep(0.2)
                
    def get_papago_result(self, driver, idx) :
        while True :
            try :
                text = self.get_one_example(driver, idx).find_element_by_css_selector(".translate_result").text.strip()
                return text
            except StaleElementReferenceException :
                Sleep(0.2)

    def get_current_page(self, driver) :
        while True :
            try :
                page = int(driver.find_element_by_css_selector(self.current_page_number).text.strip())
                return page
            except NoSuchElementException :
                return 0
            except StaleElementReferenceException :
                Sleep(0.2)

    def CheckExistence(self, WebElements, selector) :
        try :
            _ = WebElements.find_element_by_css_selector(selector)
            return True
        except NoSuchElementException :
            return False
    
    def get_webdriver(self) :
        if self.browser_type == "firefox" :
            if self.headless_mode :
                options = FirefoxOptions()
                options.add_argument("--headless")
                return webdriver.Firefox(options = options, log_path = self.logs_folder / "geckodriver.log")
            else :
                return webdriver.Firefox(log_path = self.logs_folder / "geckodriver.log")
        else :
            if self.headless_mode :
                options = ChromeOptions()
                options.add_argument("--headless")
                return webdriver.Chrome(options = options,
                        service_args = ["--verbose", "--log-path=" + str(self.logs_folder / "chromedriver.log")])
            else :
                return webdriver.Chrome(service_args = ["--verbose", "--log-path=" + str(self.logs_folder / "chromedriver.log")])
            
    def start_crawling(self) :
        driver = self.get_webdriver()
        driver.implicitly_wait(3)
        
        self.logger.StartCrawling(list(self.words_dic.keys()))
        try :
            for word in list(self.words_dic.keys()) :
                self.logger.StartWordCrawling(word)
                
                levels = self.words_dic[word]["levels"]
                start_pages = self.words_dic[word]["start_page"]
                end_pages = self.words_dic[word]["end_page"]
                user = self.words_dic[word]["user"]
                trsl = self.words_dic[word]["trsl"]

                words_dic = dict()
                for level, start_page, end_page, use_user, use_trsl  in zip(levels, start_pages, end_pages, user, trsl) :
                    previous_page = start_page - 1
                    for page in range(start_page, end_page + 1) :
                        # 해당 page로 이동
                        driver.get(self.query.format(page, word, self.levels_dic[level]))

                        try : # 본문이 나타날 때까지 기다림
                            WebDriverWait(driver, self.patience_time).until(EC.presence_of_element_located((By.ID, "searchPage_example")))
                        except TimeoutException :
                            self.logger.NoExamples(word, self.query.format(page, word, self.levels_dic[level]))
                            break

                        cur_page = self.get_current_page(driver)
                        if cur_page == 0 or cur_page < start_page : # 해당 page까지 예문이 존재하지 않음
                            self.logger.ReasonToBreak("해당 page까지 예문이 존재하지 않습니다.\n")
                            break
                        elif (previous_page != start_page - 1) and (previous_page == cur_page) : # 더이상 이동할 page가 없음
                            self.logger.ReasonToBreak("더 이상 이동할 page가 없습니다.\n")
                            break

                        self.logger.CurrentStatus(word, level, cur_page)
                        previous_page = cur_page
                        
                        for idx in range(len(driver.find_elements_by_css_selector(self.examples_area))) :
                            user_status = self.CheckExistence(self.get_one_example(driver, idx), ".user_profile")
                            trsl_status = self.CheckExistence(self.get_one_example(driver, idx), ".translate_btns")
                            
                            if trsl_status : # 파파고 번역
                                if use_trsl :
                                    self.get_one_example(driver, idx).find_element_by_css_selector(".btn_papago").click()
                                    try :
                                        WebDriverWait(driver, self.patience_time).until(
                                            lambda wd : self.get_papago_result(driver, idx) != ""
                                        )
                                        eng = self.get_eng_area(driver, idx)
                                        kor = self.get_papago_result(driver, idx)

                                        self.saver.save((word, eng, kor, "자동 번역", page, level, korea_time()))
                                    except TimeoutException :
                                        self.saver.save((word, eng, kor, "자동 번역 실패(응답 없음)", page, level, korea_time()))

                            elif user_status : # 유저 참여 번역
                                if use_user :
                                    eng = self.get_eng_area(driver, idx)
                                    kor = self.get_kor_area(driver, idx)
                                    self.saver.save((word, eng, kor, "이용자 참여", page, level, korea_time()))
                                    
                            else : # Official 또는 한글 예문이 존재하지 않음
                                eng = self.get_eng_area(driver, idx)
                                try :
                                    kor = self.get_kor_area(driver, idx)
                                    self.saver.save((word, eng, kor, "공식 예문", page, level, korea_time()))

                                except IndexError : # 한글 예문 없음
                                    kor = "None"
                                    self.saver.save((word, eng, kor, "한글 예문 없음", page, level, korea_time()))

                            # 다음 예문으로 이동하기 전 휴식
                            Sleep(self.sleep_time)

        except KeyboardInterrupt :
            self.logger.KeyboardInterruptError()

        self.saver.quit_db()
        driver.close()