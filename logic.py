from enum import Enum, auto
from typing import Any, Dict, Optional
from bs4 import BeautifulSoup
from client import MoodleQuestion


class QuestionType(Enum):
    SINGLE_CHOICE = auto()
    MULTI_CHOICE = auto()
    MATCH = auto()
    TRUEFALSE = auto()
    GAP_SELECT = auto()


def get_question_type(question: MoodleQuestion) -> Optional[QuestionType]:
    soup = BeautifulSoup(question._raw)

    if (soup.find('div', {'class': ['multichoice', 'multichoiceset']})):
        answer = soup.find('div', {'class': 'answer'})

        if answer:
            return QuestionType.MULTI_CHOICE if answer.find('input', {'type': 'checkbox'}) else QuestionType.SINGLE_CHOICE  # type: ignore

    if (soup.find('div', {'class': 'truefalse'})):
        return QuestionType.TRUEFALSE

    if (soup.find('div', {'class': 'match'})):
        return QuestionType.MATCH

    if (soup.find('div', {'class': 'gapselect'})):
        return QuestionType.GAP_SELECT

    return None


def build_random_answer(question: MoodleQuestion) -> Optional[Dict[str, Any]]:
    question_type = get_question_type(question)

    if not question_type:
        return None

    if question_type == QuestionType.SINGLE_CHOICE or question_type == QuestionType.TRUEFALSE:
        return {
            f'{question.identifier}_answer': 0
        }

    if question_type == QuestionType.MULTI_CHOICE:
        count = 0

        while f'"{question.identifier}_choice{count}"' in question.raw:
            count += 1

        return dict(zip([f'{question.identifier}_choice{index}' for index in range(count)], [1] * count))

    if question_type == QuestionType.MATCH:
        count = 0

        while f'"{question.identifier}_sub{count}"' in question.raw:
            count += 1

        return dict(zip([f'{question.identifier}_sub{index}' for index in range(count)], [*range(1, count + 1)]))

    if question_type == QuestionType.GAP_SELECT:
        count = 0

        while f'"{question.identifier}_p{count + 1}"' in question.raw:
            count += 1

        return dict(zip([f'{question.identifier}_p{index + 1}' for index in range(count)], [1] * count))
