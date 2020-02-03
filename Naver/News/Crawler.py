from __future__ import print_function
from argparse import ArgumentParser, RawTextHelpFormatter
from Model import *

'''
    -p, --period    : 해당 기간의 news들을 crawling         (default : None)
    -f, --folder    : output을 저장할 folder location       (default : current directory)
    -s, --sleep     : sleep 간격                            (default : 1초)
'''

parser = ArgumentParser(formatter_class = RawTextHelpFormatter)

parser.add_argument('-p', '--period', type = str, default = None,
    help = "해당 기간의 news들을 crawling (YYYYMMDD 형식으로 입력) ex) \"20191011 10191111\"\n")

parser.add_argument('-f', '--folder', type = str, default = None,
    help = "Crawling한 뉴스를 저장할 folder 위치\n")

parser.add_argument('-s', '--sleep', type = int, default = 1,
    help = "Crawling하는 뉴스 사이의 휴식 간격 (단위 : 초)\n")

args                        = parser.parse_args()
kwargs                      = vars(args)

crawler = Cralwer(**kwargs)
crawler.start_crawling()