from pathlib import Path
import csv
import sqlite3

class Saver() :
    def __init__(self, words_folder, logger, csv_file = None, db_file = None) :
        self.create_files(words_folder, csv_file, db_file)
        self.logger = logger
        
    def create_files(self, words_folder, csv_file, db_file) :
        if csv_file is None :
            self.csv_file = words_folder / "result.csv"
            if not self.csv_file.exists() : # 기존에 result.csv 파일이 존재하지 않았다면 header 생성
                with self.csv_file.open("w", newline = '', encoding = "utf-8") as csv_file :
                    fieldnames = ["words", "eng", "kor", "category", "page", "level", "date"]
                    writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
                    writer.writeheader()
        else :
            self.csv_file = Path(csv_file).resolve()
            
        if db_file is None :
            self.db_file = words_folder / "result.db"
            status = self.db_file.exists()
            self.conn = sqlite3.connect(self.db_file)
            self.cur = self.conn.cursor()
            if not status : # 기존에 result.db 파일이 존재하지 않았다면 table 생성
                self.cur.execute('''CREATE TABLE dictionary 
                    (_id integer primary key autoincrement, word text not null, 
                    eng text not null, kor text not null, 
                    category text not null, page integer not null, level text not null, 
                    date datetime default current_timestamp, 
                    unique (eng, kor)
                    )''')
        else :
            self.db_file = Path(db_file).resolve()
            self.conn = sqlite3.connect(self.db_file)
            self.cur = self.conn.cursor()
            
        self.query = "INSERT INTO dictionary (word, eng, kor, category, page, level, date) VALUES (?, ?, ?, ?, ?, ?, ?)"

    def quit_db(self) :
        self.conn.close()

    def save(self, data) :
        try :
            self.cur.execute(self.query, data)
            self.conn.commit()
        except sqlite3.IntegrityError :
            self.logger.AlreadyExists(data[1], data[2])
        else : # 중복된 data가 아닌 경우에만 csv file에 저장
            with self.csv_file.open("a+", newline = '', encoding = "utf-8") as csv_file :
                fieldnames = ["word", "eng", "kor", "category", "page", "level", "date"]
                writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
                writer.writerow({
                    "word" : data[0], "eng" : data[1], "kor" : data[2], "category" : data[3],
                    "page" : data[4], "level" : data[5], "date" : data[6]})