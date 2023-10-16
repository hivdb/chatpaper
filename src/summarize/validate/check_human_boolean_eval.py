from src.file_format import load_csv
from src.table import group_records_by
from ..by_question import seperate_questions


def check_human_boolean_eval(f):

    table = load_csv(f)

    boolean_questions = seperate_questions(table)['boolean']

    for question_id, rows in group_records_by(
            boolean_questions, 'question_id').items():

        human_answer = [
            i['human_answer']
            for i in rows
        ]

        if not validate_boolean(human_answer):

            print('Error, boolean question got non boolean answer.')
            print(f, question_id)


def validate_boolean(human_answer):

    boolean_answer = [
        (
            (i.lower() == 'yes') or
            (i.lower().startswith('yes,')) or
            (i.lower() == 'no') or
            (i.lower().startswith('no,'))
        )
        for i in human_answer
    ]

    if (not all(boolean_answer)):
    # if any(boolean_answers) and (not all(boolean_answers)):
        return False

    return True


# TODO validate numerical and categorical
