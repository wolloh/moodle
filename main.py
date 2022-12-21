from auth import auth, restore_session, save_session
from client import MoodleClient
from os.path import exists
from datetime import datetime
from logic import build_random_answer
import re
import uuid


LOGIN = ''
PASSWORD = ''
COURSE_MODULE_ID = 1076928
SESSION_FILENAME = 'session.dat'
QUESTIONS_COUNT = 40


def save_attempt_review(client: MoodleClient, review_text: str) -> None:
    def save_and_replace(match: re.Match[str]) -> str:
        old_filename = match[1]
        new_filename = f'{uuid.uuid4()}.jpg'

        with open(new_filename, 'wb') as file:
            file.write(client.get_content(old_filename))

        return match[0].replace(old_filename, new_filename)

    review_text = re.sub(r'<img src="(https://edu\.vsu\.ru/pluginfile\.php/\d+/question.*?)"', save_and_replace, review_text)

    with open(f'{datetime.now():%d_%m_%y__%H_%M_%S}.html', 'w', encoding='utf-8') as file:
        file.write(review_text)


if not exists(SESSION_FILENAME):
    save_session(SESSION_FILENAME, auth(LOGIN, PASSWORD))

session = restore_session(SESSION_FILENAME)
client = MoodleClient(session)

while True:
    try:
        attempt = client.start_attempt(COURSE_MODULE_ID)

        for page in range(QUESTIONS_COUNT):
            question = client.get_question(attempt, COURSE_MODULE_ID, page)
            answer = build_random_answer(question)

            if answer:
                client.send_answer(question, attempt, COURSE_MODULE_ID, answer)

        review_text = client.finish_attempt(attempt, COURSE_MODULE_ID)
        save_attempt_review(client, review_text)
    except Exception as ex:
        session = auth(LOGIN, PASSWORD)
        save_session(SESSION_FILENAME, session)

        client = MoodleClient(session)
