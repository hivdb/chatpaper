from src.table import group_records_by
from ..validate.check_human_boolean_eval import validate_boolean


def by_boolean(questions):

    reports = []

    for question_id, rows in group_records_by(
            questions, 'question_id').items():
        question_type = rows[0]['question_type']

        human_answer = [
            i['human_answer']
            for i in rows
        ]

        report = {
            'question_id': question_id,
            'question': rows[0]['question'],
            'question_type': question_type,
        }

        if not validate_boolean(human_answer):

            report['GT_Yes'] = 'Some of them are not boolean values.'
            reports.append(report)

            continue

        num_yes = len([
            i
            for i in human_answer
            if i.lower().startswith('yes')
        ])

        # TODO translate human_NA
        num_na = len([
            i
            for i in human_answer
            if i.lower().startswith('no, not mention')
        ])

        num_no = len(human_answer) - num_yes - num_na

        report['# GT_Yes'] = num_yes
        report['% GT_Yes'] = f'{round(num_yes * 100 / len(human_answer))}%'

        report['# GT_No'] = num_no
        report['% GT_No'] = f'{round(num_no * 100 / len(human_answer))}%'

        report['# GT_NA'] = num_na
        report['% GT_NA'] = f'{round(num_na * 100 / len(human_answer))}%'

        reports.append(report)

    return reports
