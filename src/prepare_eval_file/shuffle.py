from src.file_format import load_csv
from src.file_format import dump_csv
from random import shuffle
from src.table import group_records_by
from src.evaluation.quick_eval import quick_eval
from src.select_content.test_set import select_test_set
from src.excel2csv import excel2csv


def shuffle_by_paper(paper=True, question=False):
    test_set_path_list = select_test_set()

    excel_file = test_set_path_list / 'evaluation' / 'gpt-4_base.xlsx'
    file_path = test_set_path_list / 'evaluation' / 'gpt-4_base.csv'
    excel2csv(excel_file, excel_file.stem)

    table = load_csv(file_path)

    report = []
    for qid, answers in group_records_by(table, 'question_id').items():

        human_answers = [
            {
                k: i[k]
                for k in [
                    'paper',
                    'question_id', 'question', 'question_type',
                    'human_answer',
                    'human_NA'
                    ]
                }
            for i in answers

        ]

        AI_answers = [
            {
                k: i[k]
                for k in [
                    'AI_reply',
                    'AI_NA',
                    'AI_answer']
            }
            for i in answers
        ]
        shuffle(AI_answers)

        for i, j in zip(human_answers, AI_answers):
            i.update(j)
            i['chat_mode'] = 'shuffle'
            report.append(i)

    [quick_eval(i) for i in report]

    save_file = file_path.parent / f'{file_path.stem}_shuffle_paper.csv'
    dump_csv(save_file, report)
