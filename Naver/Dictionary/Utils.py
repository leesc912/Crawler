import sys
from json import dumps
from time import time, sleep
from datetime import datetime, timedelta

def Sleep(sleep_time) :
    start = time()
    while (time() - start < sleep_time) :
        sleep(sleep_time - (time() - start))
            
def korea_time(time_format = "%Y/%m/%d %H:%M:%S") :
    return (datetime.utcnow() + timedelta(hours = 9)).strftime(time_format)
            
def save_json_data(fname, data) :
    with fname.open("w", encoding = 'utf-8') as fp :
        json_data = dumps(data, indent = 4, ensure_ascii = False)
        fp.write(json_data)

def get_pages(pages, logger) :
    # 기본적으로 1 page부터 100 page까지 크롤링
    start_page, end_page = 1, 100
    if pages is not None :
        if len(pages) == 1 :
            end_page = pages[0]
        elif len(pages) == 2 :
            start_page, end_page = pages
            if start_page > end_page :
                start_page, end_page = end_page, start_page
        else :
            logger.TooManyPagesError(sys._getframe().f_lineno, pages)

    if (start_page > end_page) or any(page < 1 for page in [start_page, end_page]) :
        logger.InvalidPagesError(sys._getframe().f_lineno, start_page, end_page)

    return start_page, end_page