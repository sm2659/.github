#!/usr/bin/env python
# coding: utf-8

# In[2]:


from bs4 import BeautifulSoup
import time,requests,re
from konlpy.tag import Okt
import pandas as pd
start_time = time.time()


#쓸데없는 스크립트 제거함수
def onlytext(string):
    string=string.replace('<div align="center">', ' ') # 이것만 따로 보기??
    #string = string.replace('<br/>', ' / ')
    string = string.replace('<br>', ' ')
    #string = string.replace('<p>', ' / ' )
    #string = string.replace('</p>', ' / ')

    length = len(string)
    tagend = 0
    count = 0
    flag = 0
    if '<' in string:
        output = ''
        for i in range(length):

            if tagend == 1 and string[i] == "<":
                output = output + string[flag:flag + count]
                tagend = 0

            elif tagend == 1 and i + 1 == length:
                output = output + string[flag:flag + count + 1]
                tagend = 0

            elif string[i] == ">":
                flag = i + 1
                count = 0
                tagend = 1

            elif string[i] != "<":
                count += 1
    else:
        output =string
    output = output.replace('[', '')
    output = output.replace(']', '')
    output = output.replace('\ufeff;', '')
    output = output.replace('\u200b', '')
    output = output.replace('&nbsp;', '')
    output = output.replace('&gt;', '')
    output = output.replace('&lt;', '')
    output = output.replace('\xa0', '')
    output = output.replace("\t", "")
    output = output.replace("\n", "")
    output = output.replace("\r", "")
    return output

#공백제거함수
def enter_tab(string):
    output = string.replace("\t", "")
    output = output.replace("\n", "")
    output = output.replace("\r", "")
    return output


errorset={}

page = 1#67
url_set = set({})



    


# In[8]:


error_cnt=0
nlp = Okt()  # Twitter 라이브러리 사용

negative=('아니다','절대','검색','그냥','듯','같다','대부분','어디서', '그렇다' ,'전혀')
regex = r'[가-힣, \s ]+'


##-----real------##
arealist=["홍대","신촌","건대","명동","명지대","강남"]
a = 0
dict1={}
while a < len(arealist):
    keywordlist = ["%s맛집 \"제 돈\""%arealist[a], "%s맛집 \"제돈\""%arealist[a], "%s맛집 \"오빠가 사준\""%arealist[a], "%s맛집 \"내돈\""%arealist[a], "%s맛집 \"내 돈 \""%arealist[a], "%s맛집 \"개인 사비\""%arealist[a]]
    list1=[]
    for keyword in keywordlist:
        start = 1

        while start <= page * 15:
            url = "https://m.search.naver.com/search.naver?where=m_blog&query=" + keyword + "&start=%d" % (start)  # blog
            source_code = requests.get(url)
            soup = BeautifulSoup(source_code.text, "lxml")
            for link in soup.find_all("a", class_="total_tit"):
                temp=link.get("href")
                if "https://m.blog.naver.com" in temp:
                    list1.append(temp)
            start += 15
        dict1[arealist[a]]=list1
        datastring = ''
    a+=1

idx=0

while idx < len(dict1):
    data = open('reviews_%s.txt'%list(dict1.keys())[idx], 'w', encoding='UTF-8')
    for url in list(dict1.values())[idx]:
        try:
            if url not in url_set:
                datastring = ''
                source_code = requests.get(url, timeout=5)
                soup = BeautifulSoup(source_code.text, "lxml")

                # 글 제목 태그 정보
                if soup.find_all("div", class_="se-component-content"):
                    title = soup.find_all("div", class_="se-title-text")[0]
                else:
                    title = soup.find_all("h3", class_="se_textarea")[0]
                post_title = ""
                for i in range(len(title.contents)):
                    post_title = post_title + str(title.contents[i])

                # 글 제목에 맛집이 포함될 때
                if "맛집" in post_title:
                    # 블로그 본문 내용 찾기
                    if soup.find_all("div", attrs={"class":"se-main-container"}):
                        article = soup.find_all("div", attrs={"class":"se-main-container"})[0]
                    else:
                        article = soup.find_all("div", attrs={"id":"postViewArea"})[0]

                    post_article = str(article)
                    mainarticle = onlytext(post_article)
                    index1 =0
                    index2 =0
                    for Searchekyword in ["제돈", "제 돈", "내돈", "내 돈", "오빠가 사준", "오빠가사준", "개인사비", "개인 사비"]:
                        KWindex = mainarticle.find(Searchekyword)
                        if KWindex != -1:
                            for a in range(KWindex, -1, -1):
                                if not re.findall(regex, mainarticle[a]):
                                    index1 = a
                                    break

                            for a in range(KWindex, len(mainarticle)):
                                if not re.findall(regex, mainarticle[a]):
                                    index2 = a
                                    break
                            sentence = mainarticle[index1 + 1:index2]
                            #print(url, sentence)

                    datastring = datastring + "real\t%s\t%s\t%s\n" % (url, list(dict1.keys())[idx], mainarticle[:index1+1] + ' ' + mainarticle[index2+1:])
                    data.write(datastring)
                    url_set.add(url)
        except:
            print("error at real")
            error_cnt+=1
    
    data.close()
    file = pd.read_csv('reviews_%s.txt'%list(dict1.keys())[idx], header=None, sep = '\t')
    file.to_csv('reviews_%s.csv'%list(dict1.keys())[idx], index=False, encoding='utf-8-sig')
    idx+=1
print(len(url_set))
print(error_cnt)


end_time = time.time()
print("모든 프로세스: %f 분" % ((end_time - start_time) / 60))

