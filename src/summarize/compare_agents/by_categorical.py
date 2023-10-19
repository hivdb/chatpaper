from src.table import group_records_by
from src.file_format import dump_csv


def compare_categorical_questions(table, save_path):
    report = []

    for question_id, rows in group_records_by(table, 'question_id').items():
        question = rows[0]['question']

        # human_answer = [
        #     i['human_answer']
        #     for i in rows
        # ]

        # human_na = [
        #     1 if i.lower().startswith('na') else 0
        #     for i in human_answer
        #     ]

        agreement = [
            i['agree?']
            for i in rows
        ]

        agreement = [
            2 if (i.lower() == 'yes') else (
                1 if i.lower() == 'yes, partial' else 0
            )
            for i in agreement
        ]

        agree = len([
            i
            for i in agreement if i
            if i == 2
        ])

        # partial_agree = len([
        #     i
        #     for i in agreement if i
        #     if i == 1
        # ])

        # human_na_disagree = len([
        #     i
        #     for i, j in zip(human_na, agreement)
        #     if not j and i
        # ])

        # AI_NA = [
        #     1 if i['AI_NA'].lower().strip() == 'yes' else 0
        #     for i in rows
        # ]

        # AI_NA_disagree = len([
        #     i
        #     for i, j in zip(AI_NA, agreement)
        #     if not j and i
        # ])

        disagree = len(agreement) - agree

        rec = {
            'question_id': question_id,
            'question': question,
            'Agree': agree,
            # 'Partial agree': partial_agree,
            'Disagree': disagree,
            # 'human_NA': human_na_disagree,
            # 'AI_NA': AI_NA_disagree,
        }
        report.append(rec)

    dump_csv(save_path, report)
