from Utils import korea_time

class Logger() :
    def __init__(self, file_name, log_file, encoding = "utf-8") :
        self.file_name = file_name
        self.log_file = log_file
        self.encoding = encoding
        
    def write(self, msg) :
        with self.log_file.open("a+", encoding = self.encoding) as fp :
            fp.write(msg)

    def Arguments(self, **kwargs) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "Log File Path = {}\n".format(self.log_file)
        for k, v in list(kwargs.items()) :
            msg += "{} = {}\n".format(k, v)
        msg += "\n" + "-- " * 10 + "\n\n"
        self.write(msg)

    def NoExamples(self, word, url) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "\n[ {} ] 단어에 대한 예문이 존재하지 않습니다.\n".format(word)
        msg += "URL : {}\n".format(url)
        msg += "\n" + "-- " * 10 + "\n\n"
        self.write(msg)

    def StartCrawling(self, words) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "Crawling을 시작합니다.\n"
        msg += "<수집할 단어>\n"
        for idx in range(len(words)) :
            msg += "[{:4d}] : {}\n".format(idx + 1, words[idx])
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)

    def StartWordCrawling(self, word) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "\n[ {} ] 단어에 대한 예문을 수집합니다.\n".format(word)
        msg += "\n" + "-- " * 10 + "\n\n"
        self.write(msg)

    def CurrentStatus(self, word, level, cur_page) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "Word : [ {} ] - Level : [ {} ] - Current Page : [{:4d}]\n".format(
            word, level, cur_page)
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)

    def AlreadyExists(self, eng, kor) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "{} -> {}\n".format(eng, kor)
        msg += "이미 database에 존재하는 예문입니다.\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)

    def ReasonToBreak(self, reason) :    
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += reason
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)

    def KeyboardInterruptError(self) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "KeyboardInterrupt\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)

    def TooManyPagesError(self, file_no, pages) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "kwargs[\"pages\"]에는 최대 2개의 숫자까지 전달 가능합니다.\n"
        msg += "입력된 pages : {}\n".format(pages)
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()

    def InvalidPagesError(self, file_no, start_page, end_page) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "잘못된 page 값\n"
        msg += "start page : [{:3d}]   end page : [{:3d}]\n".format(start_page, end_page)
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()        

    def NoInputsError(self, file_no) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "kwargs[\"words\"], kwargs[\"file\"] 모두 입력되지 않았습니다.\n"
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()
        
    def InvalidLineError(self, file_no, inputs) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "Input file에 잘못된 입력값이 있습니다.\n"
        msg += "입력값 : {}\n".format(inputs)
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()
        
    def InvalidSetError(self, file_no, word, inputs) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "Input file의 단어 [ {} ]에 잘못된 입력값이 있습니다.\n".format(word)
        msg += "입력값 : {}\n".format(inputs)
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()
        
    def FileNotExistsError(self, file_no, file_path) :
        msg = "Time : [ {} ]\n".format(korea_time())
        msg += "File Name : {}   Line : {}\n".format(self.file_name, file_no)
        msg += "파일 [ {} ]가 존재하지 않습니다.\n".format(file_path)
        msg += "프로그램을 종료합니다...\n"
        msg += "\n" + " -- " * 10 + "\n\n"
        self.write(msg)
        
        self._quit()
    
    def _quit(self) :
        print("\nError가 발생했습니다.")
        print("자세한 내용은 [ {} ]을 확인해주세요.\n".format(self.log_file))
        quit()