import html2text
import os


def find_between(s, first, last):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        if(last==''):
            end=len(s)
        return s[start:end]
    except ValueError:
        return ""

j=0
while(os.path.isfile(f'output{j}.txt')):
    with open(f'output{j}.txt',encoding="utf8") as f:
        lines = f.readlines()
    s=''.join((lines))
    seprLines=s.split("<div id=\"question-")
    listQuestions=[]
    cleanList=[]
    for item in seprLines:
        sClean=html2text.html2text(item)
        cleanList.append(sClean)
        parseQ=find_between(sClean,'Текст вопроса','Отзыв').replace("\n", " ")
        if(parseQ==''):
            parseQ=find_between(sClean,'Текст вопроса','Ответ').replace("\n"," ")
        if(parseQ==''):
            parseQ=find_between(sClean,'Текст вопроса','').replace("\n"," ")
        # if(parseQ==''):
        #     parseQ=find_between(sClean,'Текст вопроса','')
        listQuestions.append(parseQ)
    # listQuestions=list(filter(None,listQuestions))
    print(listQuestions)
    j+=1
