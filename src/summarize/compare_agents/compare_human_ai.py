from src.file_format import load_csv
from .by_boolean import compare_boolean_questions
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

    compare_boolean_questions(
        question_group['boolean'],
        save_path / f'{data_file.stem}.compare.bool.csv')
    compare_numerical_questions(
        question_group['numerical'],
        save_path / f'{data_file.stem}.compare.num.csv'
        )
    compare_categorical_questions(
        question_group['categorical'],
        save_path / f'{data_file.stem}.compare.cat.csv')


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
