### Crawler.py

crawling에 대한 arguments를 전달 받아 crawler에게 전달함.
crawling할 단어들을 전달하는 방법에는 2가지가 있음.  
1. "**-F**", "**--file**" : text 파일에 crawling할 단어들이 저장되어 있음  
2. "**-w**", "**--words**" : terminal에 crawling할 단어들을 직접 입력

"**--words**" arguments를 사용할 경우, 세부 설정(**"-p", "-l", "-u", "-t"**)이 모든 단어에 똑같이 적용됨.  
각 단어마다 자세한 설정을 하고 싶은 경우에는 "**--file**" arugments 사용하기.   

---

##### ex1

    python Crawler.py -w "i" "we" "he" "she" "they" -p 50 -l "초급" "고급" -u "True" -t "False"

모든 단어(i, we, he, she, they)에 대해  
각 단계(초급, 고급)마다 최대 50 page까지 크롤링하고  
유저가 참여한 번역과 파파고 번역 결과를 포함함.  

##### ex2

    python Cralwer.py -w "i" "we" -p 20 40 -l "중급" -u "False" -t "False"

모든 단어(i, we)에 대해  
중급 단계에서 20 page부터 40 page까지 크롤링  

##### ex3

    python Crawler.py -F "/foo/bar/crawling.txt"

```
# line 처음에 '#' 문자가 들어간 line은 Crawler가 무시함
# "/" 문자를 기준으로 각 단계가 나뉨
# 각 단계별 설정은 순서대로 표현 수준, 페이지 범위, 유저가 참여한 번역 포함 여부, 파파고 번역 포함 여부이며 띄어쓰기로 구분됨

i / 초급 40 true false / 중급 20 false true / 고급 50 true true
# we / 초급 100 false false / 고급 100 false false
they / 고급 30 true true
she / 중급 20-40 true true / 고급 10-100 false false
```

**i** :  

 - 초급 : 최대 40 page까지 크롤링 (유저 번역 포함)
 - 중급 : 최대 20 page까지 크롤링 (파파고 번역 포함)
 - 고급 : 최대 50 page까지 크롤링 (유저와 파파고 번역 모두 포함)
    
**we** : 

 - 크롤링하지 않음  

**they** : 

 - 고급 : 최대 30 page까지 크롤링 (유저와 파파고 번역 모두 포함)  

**she** :

 - 중급 : 20 page부터 40 page까지 크롤링 (유저와 파파고 번역 모두 포함)
 - 고급 : 10 page부터 100 page까지 크롤링

##### 공통 사항

1. 맞춤법이 틀릴 경우(쵸급, 고금, Truee, flase 등등...) **error** 발생

---

#### input file을 전달할 때의 주의점

1. **중복된 표현 수준(초급, 중급, 고급)이 존재할 경우 앞 부분의 설정만 사용**

```
# "초급 100 false true"는 사용하지 않음
i / 초급 40 true true / 초급 100 false true /
```

1. **최대 3개 까지의 설정만 사용**

```
# "중급 20 true false" 와 "고급 20 false false"는 사용하지 않음
i / 초급 40 true false / 중급 30 true false / 중급 20 true false / 고급 100 true true / 고급 20 false false
```

3. **같은 단어가 존재할 경우 먼저 위치한 단어의 설정만 사용**

```
# "i / 초급 20 true true / 중급 40 false false / 고급 10 true false"만 사용
i / 초급 20 true true / 중급 40 false false / 고급 10 true false
i / 중급 60 false false
```