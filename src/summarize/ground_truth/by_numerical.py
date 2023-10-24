from src.table import group_records_by


def by_numerical(questions):

    report_table = []

    for question_id, rows in group_records_by(questions, 'question_id').items():
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

        num_not_zero = len([
            i
            for i in human_answer
            if str(i.lower()) != '0'
            ])

        report['# GT_nonzero'] = num_not_zero
        report['% GT_nonzero'] = (
            f'{round(num_not_zero * 100 / len(human_answer))}%')

        report['# same'] = len(set(human_answer))

        # TODO, show all results
        report_table.append(report)

    return report_table
