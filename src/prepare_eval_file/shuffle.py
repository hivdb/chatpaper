from src.file_format import load_csv
from src.file_format import dump_csv
from random import shuffle
from src.table import group_records_by
from src.evaluation.quick_eval import quick_eval


def shuffle_by_paper(file_path, paper=True, question=False):

    table = load_csv(file_path)

    report = []
    for qid, answers in group_records_by(table, 'question_id').items():

        human_answers = [
            {
                k: i[k]
                for k in [
                    'paper',
                    'question_id', 'question', 'question_type',
                    'human_answer', 'human_NA']
                }
            for i in answers

        ]

        AI_answers = [
            {
                k: i[k]
                for k in ['AI_reply', 'AI_NA', 'AI_answer']
            }
            for i in answers
        ]
        shuffle(AI_answers)

        for i, j in zip(human_answers, AI_answers):
            i.update(j)
            report.append(i)

    [quick_eval(i) for i in report]

    save_file = file_path.parent / f'{file_path.stem}.shuffle_paper.csv'
    dump_csv(save_file, report)
