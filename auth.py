from dataclasses import dataclass
import json
from requests.cookies import RequestsCookieJar
import requests as req
import re
from constants import DOMAIN
from utils import DataclassJSONEncoder, dict_to_dataclass


@dataclass(frozen=True)
class MoodleSession:
    session_key: str
    moodle_session_cookie: str


@dataclass(frozen=True)
class _AuthPreparationResult:
    login_token: str
    auth_cookies: RequestsCookieJar


def auth(login: str, password: str) -> MoodleSession:
    auth_preparation_result = _get_auth_preparation_result()

    data = {
        'achor': '',
        'logintoken': auth_preparation_result.login_token,
        'username': login,
        'password': password
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = req.post(f'https://{DOMAIN}/login/index.php',
                        cookies=auth_preparation_result.auth_cookies, headers=headers, data=data)

    return MoodleSession(_get_api_token_key(response.text), response.history[0].cookies['MoodleSession'])


def save_session(filename: str, session: MoodleSession) -> None:
    with open(filename, "w") as file:
        json.dump(session, file, cls=DataclassJSONEncoder)


def restore_session(filename: str) -> MoodleSession:
    with open(filename, 'r') as file:
        return dict_to_dataclass(MoodleSession, json.loads(file.read()))


def _get_auth_preparation_result() -> _AuthPreparationResult:
    response = req.get(f'https://{DOMAIN}/login/index.php')

    match = re.search(
        r'<(?:.*?)name="logintoken"(?:.*?)value="(.*?)">', response.text)

    if not match:
        raise ValueError('Unable to get LoginToken.')

    return _AuthPreparationResult(match[1], response.cookies)


def _get_api_token_key(html: str) -> str:
    match = re.search(r'<(?:.*?)name="sesskey"(?:.*?)value="(.*?)">', html)

    if not match:
        raise ValueError('Unable to get LoginToken.')

    return match[1]
