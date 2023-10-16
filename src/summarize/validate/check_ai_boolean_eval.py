from src.file_format import load_csv
from ..by_question import seperate_questions


def check_ai_boolean_eval(f):
    table = load_csv(f)
    questions = seperate_questions(table)

    by_boolean(questions['boolean'], f)


def by_boolean(questions, f):

    for i in questions:

        question_id = i['question_id']

        agreement = i['agree?']
        c = 1 if (agreement.lower() == 'yes') else 0

        human_answer = i['human_answer']
        human_na = True if i['human_NA'].lower() == 'yes' else False
        h = translate_boolean(human_answer)

        AI_answer = i['AI_answer']
        ai_na = True if i['AI_NA'].lower() == 'yes' else False
        a = translate_boolean(AI_answer)

        if c:
            if h == 'yes' and h != a:
                print_error(locals())
            elif (
                    h in ('no', 'na') and
                    a not in ('no', 'na')):
                print_error(locals())
            elif h == 'no, not na' and a != 'no':
                print_error(locals())
        else:
            if (h in ('yes', 'no', 'na') and
                    h == a):
                print_error(locals())
            if h == 'no, not na' and a == 'no':
                print_error(locals())


# def by_boolean_error(agreement, human_answer, human_na, ai_answer, ai_na):

#     if agreement:
#         if human_na and ai_na:
#             return True

#         if human_na and (not ai_na:





def print_error(context):

    i = context['i']
    question_id = context['question_id']
    agreement = context['agreement']
    human_answer = context['human_answer']
    AI_answer = context['AI_answer']

    print('Error on agreement')
    print(i['paper'], question_id)
    print(agreement, human_answer, AI_answer)


def translate_boolean(value):

    value = value.lower()

    if value in ('yes', 'no', 'na'):
        return value

    if value.startswith('yes'):
        return 'yes'

    if value.startswith('no, not'):
        return 'na'

    if value.startswith('na'):
        return 'na'

    if len(value.replace('no,', '').strip()) > 0:
        return 'no'

    return 'no'
