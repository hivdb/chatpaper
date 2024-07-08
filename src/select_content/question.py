from ..preset import QUESTION_PATH
from ..file_format import load_csv
from prompt_toolkit.shortcuts import checkboxlist_dialog
from prompt_toolkit.shortcuts import radiolist_dialog
from src.exceptions import check_selection
from src.preset import DEFAULT_OPTIONS


def load_questions(file_path):
    questions = {}

    for i in load_csv(file_path):
        if 'use' in i:
            if i['use'].lower() != 'yes':
                continue

        question = i['question'].strip()
        cheatsheet = i.get('cheatsheet', '').strip()
        prompt = i.get('prompt', '').strip()

        if prompt:
            questions[i['id']] = f"```{prompt}\n\n\n{question}````\n\n"
        elif cheatsheet:
            questions[i['id']] = f"```{cheatsheet}\n\n\n{question}````\n\n"
        else:
            questions[i['id']] = question

    return questions


def list_question_set(folder=QUESTION_PATH):

    result = []
    for i in folder.iterdir():
        if i.name.startswith('.'):
            continue

        if i.suffix not in ('.csv'):
            continue

        if i.name.startswith('_'):
            continue

        result.append((i, i.stem.capitalize()))

    return result


def select_question_set(
        title='Select question set'):

    if 'question_set' in DEFAULT_OPTIONS:
        return QUESTION_PATH / f'{DEFAULT_OPTIONS.get("question_set")}.csv'

    result = radiolist_dialog(
        title=title,
        text='',
        values=list_question_set(),
    ).run()

    return result


def select_question(question_set, all_option=False):

    questions = select_some_question(question_set, all_option=all_option)

    if 'all' in questions:
        return load_questions(question_set)
    else:
        return {
            i[0]: i[1]
            for i in questions
        }


@check_selection()
def select_some_question(
        question_set,
        title="Please select your question", all_option=False):

    if 'questions' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('questions')

    # TODO, show question id
    questions = [
        ((i, j), f"{i}. {j}")
        for i, j in load_questions(question_set).items()
    ]
    num_ques = len(questions)

    if all_option:
        questions.insert(0, ('all', 'All'))

    result = checkboxlist_dialog(
        title=title,
        text=f'{num_ques} questions',
        values=questions,
    ).run()

    return result


def load_next_question(prev_question, ques_folder):
    # TODO, tree structured questions
    pass
