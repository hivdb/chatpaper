from src.file_format import load_csv
from .by_boolean import compare_boolean_questions
from .by_boolean import get_triple_cont_table
from .by_categorical import compare_categorical_questions
from .by_numerical import compare_numerical_questions
from ..by_question import seperate_questions


def compare_human_and_ai(data_file_list, save_path):

    for i in data_file_list:
        get_contigency_table(i, save_path)


def get_contigency_table(data_file, save_path):

    question_group = seperate_questions(load_csv(data_file))

    # TODO human NA column
    # TODO different ways of NA depends on the question

    print(data_file)
    compare_boolean_questions(
        question_group['boolean'],
        save_path / f'{data_file.stem}.compare.bool.csv')
    calc_F1_score_for_boolean(question_group['boolean'])
    compare_numerical_questions(
        question_group['numerical'],
        save_path / f'{data_file.stem}.compare.num.csv'
        )
    calc_F1_score_for_non_boolean(question_group['numerical'])
    compare_categorical_questions(
        question_group['categorical'],
        save_path / f'{data_file.stem}.compare.cat.csv')
    calc_F1_score_for_non_boolean(question_group['categorical'])


def calc_F1_score_for_boolean(table):
    human_answer = [
            i['human_answer']
            #  i['human_NA'])
            for i in table
        ]

    AI_answer = [
        i['AI_answer']
        for i in table
    ]

    human_answer = [
        # (
        1 if (
            (i.lower() == 'yes') or
            (i.lower().startswith('yes,'))
        ) else 0
            # 1 if (
            #     j.lower() == 'yes'
            # ) else 0
        # )
        for i in human_answer
    ]

    AI_answer = [
        1 if (
            (i.lower() == 'yes') or
            (i.lower().startswith('yes,'))
        ) else 0
        for i in AI_answer
    ]

    cont_table = get_triple_cont_table(human_answer, AI_answer)
    print(cont_table)
    recall = cont_table['H_Y_AI_Y'] / (
        cont_table['H_Y_AI_Y'] + cont_table['H_Y_AI_N'])
    precision = cont_table['H_Y_AI_Y'] / (
        cont_table['H_Y_AI_Y'] + cont_table['H_N_AI_Y'])
    f1_score = 2 * precision * recall / (precision + recall)
    print('recall', recall * 100)
    print('precision', precision * 100)
    print('f1_score', f1_score * 100)


def calc_F1_score_for_non_boolean(table):

    agreement = [
        i['agree?']
        for i in table
    ]
    agreement = [
        1 if (i.lower() == 'yes') else 0
        for i in agreement
    ]

    agree = len([
        i
        for i in agreement if i
    ])

    disagree = (len(agreement) - agree)

    print(agree, disagree)
    recall = agree / (agree + disagree)
    precision = agree / (agree + disagree)
    f1_score = 2 * precision * recall / (precision + recall)
    print('recall', recall * 100)
    print('precision', precision * 100)
    print('f1_score', f1_score * 100)


# TODO add a note of this algorithm
# def detect_question_type():

#     for _, rows in group_records_by(table, 'question_id').items():

#         question = rows[0]['question']

#         human_answer = [
#             i['human answer']
#             for i in rows
#         ]

#         boolean_answers = [
#             (
#                 (i.lower() == 'yes') or
#                 (i.lower().startswith('yes,')) or
#                 (i.lower() == 'no') or
#                 (i.lower().startswith('no,'))
#             )
#             for i in human_answer
#         ]

#         if not any(boolean_answers):
#             if question.lower().startswith('how many'):
#                 num_q.extend(rows)
#             else:
#                 cat_q.extend(rows)
#         else:
#             bool_q.extend(rows)
