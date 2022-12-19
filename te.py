import json
import pdfkit
import requests
import ijson
import time

def finishAttempt(attemptId,token):
    response=session.get(f'https://edu.vsu.ru/webservice/rest/server.php?moodlewsrestformat=json&wstoken={token}&wsfunction=mod_quiz_process_attempt&attemptid={attemptId}&finishattempt=1')
    data=response.json()
    flag=False
    if(response.status_code==200 and data['state']=='finished'):
        flag=True
    return flag

def getNewAttempt(token):
    newAttempt=session.get(f'https://edu.vsu.ru/webservice/rest/server.php?moodlewsrestformat=json&wstoken={token}&wsfunction=mod_quiz_start_attempt&quizid=64588')
    data=json.loads(newAttempt.content)
    return data['attempt']['id']
def getToken(username,password):
    data=session.get(f'https://edu.vsu.ru/login/token.php?username={username}&password={password}&service=moodle_mobile_app')
    token = data.json()
    return token['token']


def saveToNotepad(attemptId,token,acumFileName):
    f=session.get(f'https://edu.vsu.ru/webservice/rest/server.php?moodlewsrestformat=json&wstoken={token}&wsfunction=mod_quiz_get_attempt_review&attemptid={attemptId}')
    data=json.loads(f.content)
    questions=data['questions']
    output_file = open(f'output'+str(acumFileName)+'.txt', 'w',encoding="utf-8")
    for question in questions:
        output_file.write(question['html'])
    output_file.close()
def saveToPdf(attemptId,token,acumFileName):
    config = pdfkit.configuration(wkhtmltopdf="C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe")
    f=session.get(f'https://edu.vsu.ru/webservice/rest/server.php?moodlewsrestformat=json&wstoken={token}&wsfunction=mod_quiz_get_attempt_review&attemptid={attemptId}')
    options = {
        'encoding': "UTF-8",
        'custom-header': [
            ('Accept-Encoding', 'gzip')
        ]
    }
    objects = ijson.kvitems(f.content, 'questions.item')
    htmls=(v for k, v in  objects if  k=='html')
    i=0
    for obj in htmls:
        pdfkit.from_string(obj, f'{"out"+str(j)+str(i)+".pdf"}',configuration=config,options=options)
        i+=1
    time.sleep(3)

j=0
while(True):
    session=requests.Session()
    token=getToken("","")
    id=getNewAttempt(token)
    if(not finishAttempt(id,token)):
        raise Exception('Cannot finish attempt')
    saveToNotepad(attemptId=id,token=token,acumFileName=j)
    j+=1





