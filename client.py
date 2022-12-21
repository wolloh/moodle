import re
from typing import Any, Dict, Optional
from auth import MoodleSession
import requests as req
import requests.cookies as cookies
from constants import DOMAIN
from http import HTTPStatus


class MoodleQuestion:
    _raw: str
    _identifier: Optional[str]
    _sequence_check: Optional[int]

    def __init__(self, question_page_text: str) -> None:
        self._raw = question_page_text
        self._identifier = None
        self._sequence_check = None

    @property
    def identifier(self) -> str:
        if not self._identifier:
            self._identifier = self._parse_identifier()

        return self._identifier

    @property
    def sequence_check(self) -> int:
        if not self._sequence_check:
            self._sequence_check = self._parse_sequence_check()

        return self._sequence_check

    @property
    def raw(self) -> str:
        return self._raw

    def _parse_identifier(self) -> str:
        match = re.search(r'<div id="question-(.*?)-(.*?)"', self._raw)

        if not match:
            raise ValueError('Unable to get id from question.')

        return f'q{match[1]}:{match[2]}'

    def _parse_sequence_check(self) -> int:
        match = re.search(r'<input.*?sequencecheck.*?/>', self._raw)

        if not match:
            raise ValueError(
                'Unable to get input tag with sequence_check from question.')

        input_tag = match[0]

        match = re.search(r'value="(.*?)"', input_tag)

        if not match:
            raise ValueError('Unable to get sequence_check from question.')

        return int(match[1])


class MoodleClient:
    _session_key: str
    _session: req.Session

    def __init__(self, session: MoodleSession) -> None:
        self._session_key = session.session_key

        self._session = req.Session()
        self._session.cookies.set_cookie(cookies.create_cookie(
            domain=DOMAIN, name='MoodleSession', value=session.moodle_session_cookie))

    def get_content(self, url: str) -> Optional[bytes]:
        response = self._session.get(url, allow_redirects=False)

        return response.content if response.status_code == HTTPStatus.OK else None

    def start_attempt(self, course_module_id: int) -> int:
        data = {
            'cmid': course_module_id,
            'sesskey': self._session_key
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self._session.post(f'https://{DOMAIN}/mod/quiz/startattempt.php',
                                      headers=headers, data=data, allow_redirects=False)

        if response.status_code != HTTPStatus.SEE_OTHER:
            raise ValueError('Unable to get attempt id.')

        match = re.search(
            r'attempt=(\d+)', response.text)

        if not match:
            raise ValueError('Unable to get attempt id.')

        return int(match[1])

    def get_question(self, attempt: int, course_module_id: int, page_id: int) -> MoodleQuestion:
        params = {
            'attempt': attempt,
            'cmid': course_module_id
        }

        if page_id > 0:
            params['page'] = page_id

        response = self._session.get(
            f'https://{DOMAIN}/mod/quiz/attempt.php', params=params)

        if response.status_code != HTTPStatus.OK:
            raise ValueError('Unable to get question page.')

        return MoodleQuestion(response.text)

    def send_answer(self, question: MoodleQuestion, attempt: int, course_module_id: int, answer_content_disposition: Dict[str, Any]) -> None:
        files = {
            'attempt': (None, attempt),
            'timeup': (None, 0),
            'sesskey': (None, self._session_key),
            f'{question.identifier}_:sequencecheck': (None, question.sequence_check)
        }

        params = {
            'cmid': course_module_id
        }

        for key, value in answer_content_disposition.items():
            files[key] = (None, value)

        self._session.post(f'https://{DOMAIN}/mod/quiz/processattempt.php',
                           params=params, files=files, allow_redirects=False)

    def finish_attempt(self, attempt: int, course_module_id: int) -> str:
        data = {
            'attempt': attempt,
            'finishattempt': 1,
            'timeup': 0,
            'slots': '',
            'cmid': course_module_id,
            'sesskey': self._session_key
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = self._session.post(f'https://{DOMAIN}/mod/quiz/processattempt.php',
                                      headers=headers, data=data)

        return response.text
