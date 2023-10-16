from ..by_question import seperate_questions
from src.file_format import load_csv


def check_NA(f):

    table = load_csv(f)

    questions = seperate_questions(table)

    by_boolean(questions['boolean'], f)
    by_numerical(questions['numerical'], f)
    by_categorical(questions['categorical'], f)


def by_boolean(questions, f):

    for i in questions:

        assert i['agree?'].lower() in ['yes', 'no', 'yes, partial']
        assert i['human_NA'].lower() in ['yes', 'no']
        assert i['AI_NA'].lower() in ['yes', 'no']

        human_NA = True if i['human_NA'].lower() == 'yes' else False
        AI_NA = True if i['AI_NA'].lower() == 'yes' else False

        AI_answer = i['AI_answer'].lower()

        if AI_NA:
            if AI_answer != 'na':
                print(f'Error AI NA {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')

        if human_NA and AI_NA:
            if not i['agree?'].lower().startswith('yes'):
                print(f'Error agree? {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')

        # IF AN_answer NA, AI_NA should be Yes


def by_numerical(questions, f):
    for i in questions:
        human_NA = True if i['human_NA'].lower() == 'yes' else False
        AI_NA = True if i['AI_NA'].lower() == 'yes' else False

        AI_answer = i['AI_answer'].lower()

        # TODO, only 0
        if AI_NA:
            if not AI_answer.isdigit():
                print(f'Error AI NA {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')
            elif int(AI_answer) != 0:
                print(f'Error AI NA {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')
        if human_NA and AI_NA:
            if not i['agree?'].lower().startswith('yes'):
                print(f'Error agree? {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')


def by_categorical(questions, f):
    for i in questions:
        human_NA = True if i['human_NA'].lower() == 'yes' else False
        AI_NA = True if i['AI_NA'].lower() == 'yes' else False

        AI_answer = i['AI_answer'].lower()

        if AI_NA:
            if AI_answer != 'na':
                print(f'Error AI NA {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')

        if human_NA and AI_NA:
            if not i['agree?'].lower().startswith('yes'):
                print(f'Error agree? {f}, {i["paper"]}, {i["question_id"]}, {i["question_type"]}')

# TODO auto translate boolean value from table
# TODO auto change case for string.
