from __future__ import print_function
from argparse import RawTextHelpFormatter, ArgumentParser
from argparse_type_check import bool_spelling_check, level_spelling_check
from Model import Crawler

parser = ArgumentParser(description = "Naver Dictionary Crawler", formatter_class = RawTextHelpFormatter)

parser.add_argument('-b', '--browser', type = str, default = "firefox",
    help = "\nCrawling을 할 때 실행할 browser\n" +
           "firefox 또는 chrome 선택 가능\n" +
           "default : firefox\n\n")

parser.add_argument('-H', '--headless', type = bool_spelling_check, default = True,
    help = "\nBrowser를 headless mode로 실행\n" +
            "default : True\n\n")

parser.add_argument('-w', '--words', nargs = '+', type = str, default = None,
    help = "\n수집할 영어 단어 - ex) -w \"i\" \"we\" \"car\"\n\n")

parser.add_argument('-F', '--file', type = str, default = None, 
    help = "\n예문을 수집할 단어들이 저장된 파일. 예제는 ReadMe 참조\n" +
            "arguments words와 file 모두 입력된 경우, file arguments만 사용\n\n")

parser.add_argument('-c', '--csv_file', type = str, default = None,
    help = "\n이미 존재하는 csv 파일에 data를 추가\n\n")

parser.add_argument('-d', '--db_file', type = str, default = None,
    help = "\n이미 존재하는 sqlite 파일에 data를 추가\n\n")

parser.add_argument('-u', '--user', type = bool_spelling_check, default = True,
    help = "\n이용자가 번역에 참여한 예문을 포함\n" +
           "default : True\n\n")

parser.add_argument('-t', '--translator', type = bool_spelling_check, default = True,
    help = "\n네이버 파파고 번역기가 번역한 예문을 포함\n" +
           "default : True\n\n")

parser.add_argument('-p', '--pages', nargs = '+', type = int, default = None,
    help = "\n한 레벨 당 저장할 최대 page 수\n" +
            "숫자 2개를 입력할 시, 크롤링 범위를 나타냄\n" +
            "ex) -p 100 (1 page에서 100 page까지 크롤링)\n" +
            "ex) -p 25 70 (25 page에서 70 page까지 크롤링)\n"
           "default : 1 page에서 100 page까지 크롤링\n\n")

parser.add_argument('-l', '--levels', nargs = '+', type = level_spelling_check, default = None,
    help = "\n한 단어 당 저장할 표현 수준 - ex) -l \"초급\", \"고급\"\n" + 
           "default : all(초급, 중급, 고급)\n\n")

parser.add_argument('-f', '--folder', type = str, default = None,
    help = "\n결과를 저장할 folder 위치\n" +
           "default : 현재 위치\n\n")

parser.add_argument('-s', '--sleep', type = float, default = 1,
    help = "\n예문과 예문 사이에 휴식 시간 (단위 : 초)\n" +
           "default : 1초\n\n")

parser.add_argument('-P', '--patience', type = float, default = 5,
    help = "\n어떤 event가 완전히 로딩될 때까지 기다릴 최대 시간(단위 : 초)\n" + 
           "default : 5초\n\n")

args                        = parser.parse_args()
kwargs                      = vars(args)

crawler = Crawler(**kwargs)
crawler.start_crawling()