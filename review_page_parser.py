# coding: utf-8
from bs4 import BeautifulSoup
import re

html_path = '123.htm'

file = open(html_path, encoding='utf8')
html_text = file.read()

def parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    raw_questions = soup.find_all('div', {'class': 'que'})
    qa_tuples = form_qa_tuples(raw_questions)
    print(qa_tuples)

def form_qa_tuples(raw_questions):
    qa_tuples = []
    debug = []
    for que in raw_questions:
        q = que.find('div', {'class': 'formulation'})
        question_soup = q.find('div', {'class': 'qtext'})
        answer_soup = q.find(['div', 'span'], {'class': ['answer', 'control']})

        question = extract_question(question_soup)
        answers_list = extract_answers(answer_soup, que)

        qa_tuples.append((question, answers_list))
        debug.append((question_soup, answer_soup))

    return qa_tuples

def extract_answers(q, que):
    choices = []
    if 'truefalse' in que.attrs['class']:
        choices = q.find_all('label')

    if 'control' in q.attrs['class']:
        choices = q.find_all('option')

    if 'ordering' in q.attrs['class']:
        choices = q.find_all('li')

    if choices:
        return [normalize_text(choice.get_text()) for choice in choices if normalize_text(choice.get_text()) not in ['']]
    else:
        return normalize_text(q.get_text()).split('\n')

def extract_question(soup):
    return normalize_text(soup.get_text()).replace('\n', ' ')

def normalize_text(text):
    return re.sub(' +', ' ', text.replace('\xa0', ' ').strip())

parse(html_text)