from src.file_format import load_csv
from src.file_format import dump_csv
from collections import defaultdict
from operator import itemgetter
from src.table import group_records_by


def compare_ai_mode_diff(save_path, data_file_list):

    date_tables = [
        load_csv(i)
        for i in data_file_list
    ]

    grouped = defaultdict(list)

    for table in date_tables:
        for row in table:
            grouped[(row['paper'], row['question_id'])].append(row)

    question_ids = list(set([
        i[1]
        for i in grouped.keys()
    ]))

    report = []
    improve = []
    worse = []
    for (paper, question_id), rows in grouped.items():

        agreement = [
            True if i['agree?'].lower().startswith('yes') else False
            for i in rows
        ]

        if all(agreement):
            continue

        report_row = {
            'paper': paper,
            'question_id': question_id,
            'question': rows[0]['question'],
            'question_type': rows[0]['question_type'],
            'human_answer': rows[0]['human_answer'],
            'human_NA': rows[0]['human_NA'],
            'same agree?': 'Yes' if len(set(agreement)) == 1 else 'No'
        }

        for i in rows:
            report_row[f"{i['chat_mode']} AI_reply"] = i['AI_reply']
            report_row[f"{i['chat_mode']} AI_NA"] = i['AI_NA']
            report_row[f"{i['chat_mode']} agree?"] = i['agree?']

        report.append(report_row)

        if len(agreement) != 2:
            continue

        if not agreement[0] and agreement[1]:
            improve.append(report_row)
        elif agreement[0] and not agreement[1]:
            worse.append(report_row)

    report.sort(key=itemgetter('question_id'))

    dump_csv(save_path / 'disagree_with_human.csv', report)

    report = [
        i
        for i in report
        if i['same agree?'].lower() != 'yes'
    ]

    dump_csv(save_path / 'mode_disagree.csv', report)

    get_change_report(save_path, report, question_ids)

    get_top_3_improve(save_path, improve)
    get_top_3_worse(save_path, worse)


def get_change_report(save_path, report, question_ids):

    improve_count = defaultdict(int)
    worse_count = defaultdict(int)

    for question_id, ques_list in group_records_by(
            report, ['question_id']).items():
        for q in ques_list:
            agreement = [
                True if j.lower() == 'yes' else False
                for i, j in q.items()
                if i.endswith('agree?') and i != 'same agree?'
            ]

            if len(agreement) != 2:
                continue

            if agreement[0] and not agreement[1]:
                worse_count[question_id] += 1
            elif not agreement[0] and agreement[1]:
                improve_count[question_id] += 1

    report = []
    for question_id in question_ids:
        report.append({
            'question_id': question_id,
            '# improve': improve_count.get(question_id, 0),
            '# worse': worse_count.get(question_id, 0),
            '# diff': (
                improve_count.get(question_id, 0) -
                worse_count.get(question_id, 0))
        })

    dump_csv(save_path / 'mode_disagree_summary.csv', report)


def get_top_3_improve(save_path, improve):

    ordered_report = list(
        group_records_by(improve, ['question_id']).items())

    ordered_report.sort(key=lambda x: len(x[-1]), reverse=True)

    top_3_question = [
        k
        for i, j in ordered_report[:3]
        for k in j
    ]

    dump_csv(save_path / 'mode_disagree_top3_improved.csv', top_3_question)


def get_top_3_worse(save_path, worse):

    ordered_report = list(
        group_records_by(worse, ['question_id']).items())

    ordered_report.sort(key=lambda x: len(x[-1]), reverse=True)

    top_3_question = [
        k
        for i, j in ordered_report[:3]
        for k in j
    ]

    dump_csv(save_path / 'mode_disagree_top3_worse.csv', top_3_question)


def get_top_3_changed(save_path, report):

    ordered_report = list(
        group_records_by(report, ['question_id']).items())

    ordered_report.sort(key=lambda x: len(x[-1]), reverse=True)

    top_3_question = [
        k
        for i, j in ordered_report[:3]
        for k in j
    ]

    dump_csv(save_path / 'mode_disagree_top3_changed.csv', top_3_question)

    # TODO remove renamed files when in development
