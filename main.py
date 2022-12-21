from typing import Any, Dict, Optional
from auth import auth, restore_session, save_session
from client import MoodleClient, MoodleQuestion
from os.path import exists
from datetime import datetime


LOGIN = ''
PASSWORD = ''
COURSE_MODULE_ID = 1076928
SESSION_FILENAME = 'session.dat'
QUESTIONS_COUNT = 40


def build_random_answer(question: MoodleQuestion) -> Optional[Dict[str, Any]]:
    # TODO:
    return None


def save_attempt_review(review_text: str) -> None:
    with open(f'{datetime.now():%d_%m_%y__%H_%M_%S}', 'w') as file:
        file.write(review_text)


if not exists(SESSION_FILENAME):
    save_session(SESSION_FILENAME, auth(LOGIN, PASSWORD))

session = restore_session(SESSION_FILENAME)
client = MoodleClient(session)

while True:
    attempt = client.start_attempt(COURSE_MODULE_ID)

    for page in range(QUESTIONS_COUNT):
        question = client.get_question(attempt, COURSE_MODULE_ID, page)
        answer = build_random_answer(question)

        if answer:
            client.send_answer(question, attempt, COURSE_MODULE_ID, answer)

    review_text = client.finish_attempt(attempt, COURSE_MODULE_ID)
    save_attempt_review(review_text)
