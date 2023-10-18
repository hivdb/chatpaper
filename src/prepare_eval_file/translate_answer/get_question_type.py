from src.file_format import load_csv
from src.preset import QUESTION_PATH


def get_question_type(report):

    questions = load_csv(QUESTION_PATH / 'Set1.csv')
    question_types = {
        i['id']: i['type']
        for i in questions
    }

    questions = {
        i['id']: i['question']
        for i in questions
    }

    for i in report:
        question = questions[i['question_id']]
        if question in i['question']:
            i['question'] = question

        i['question_type'] = question_types[i['question_id']]

    return report
