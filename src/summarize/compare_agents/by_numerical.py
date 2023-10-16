from src.table import group_records_by
from src.file_format import dump_csv


def compare_numerical_questions(table, save_path):
    report = []

    # human_answer = [
    #     i.strip()
    #     for i in human_answer
    # ]
    # human_answer = [
    #     (i if i.find(',') == -1 else i[:i.find(',')]) if (
    #         i.startswith('0') or i.startswith('NA')
    #     ) else i
    #     for i in human_answer
    # ]
    # human_answer = [
    #     re.sub(r'\(\w*\)', '', i).strip()
    #     for i in human_answer
    # ]

    for question_id, rows in group_records_by(table, 'question_id').items():
        question = rows[0]['question']

        human_answer = [
            i['human_answer']
            for i in rows
        ]

        AI_NA = [
            1 if i['AI_NA'].lower().strip() == 'yes' else 0
            for i in rows
        ]

        human_na = [
            1 if i.lower().startswith('na') else 0
            for i in human_answer
        ]

        agreement = [
            i['agree?']
            for i in rows
        ]
        agreement = [
            1 if (i.lower() == 'yes') else 0
            for i in agreement
        ]

        agree = len([
            i
            for i in agreement if i
        ])

        human_na_disagree = len([
            i
            for i, j in zip(human_na, agreement)
            if not j and i
        ])

        AI_NA_disagree = len([
            i
            for i, j in zip(AI_NA, agreement)
            if not j and i
        ])

        disagree = (
            len(agreement) - agree - human_na_disagree -
            AI_NA_disagree)

        rec = {
            'question_id': question_id,
            'question': question,
            'Agree': agree,
            'Disagree': disagree,
            'human_NA': human_na_disagree,
            'AI_NA': AI_NA_disagree,
        }
        report.append(rec)

    dump_csv(save_path, report)
