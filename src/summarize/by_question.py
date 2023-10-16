from src.file_format import load_csv
from src.file_format import dump_csv
from src.table import group_records_by
from statistics import median
from collections import defaultdict


def seperate_questions(table):

    return {
        'boolean': [
            i
            for i in table
            if i['question_type'] == 'Boolean'
        ],
        'numerical': [
            i
            for i in table
            if i['question_type'] == 'Numerical'
        ],
        'categorical': [
            i
            for i in table
            if i['question_type'] == 'Categorical'
        ],
    }


def summarize_by_question(table_path):
    table = load_csv(table_path)

    num_paper = len(set(
        i['paper']
        for i in table
    ))

    summary = []

    cal_median = defaultdict(list)

    headers = list(table[0].keys())
    headers.remove('paper')
    headers.remove('question_id')
    headers.remove('question_type')
    headers.remove('question')
    headers.remove('# agree')

    for q, q_list in group_records_by(table, 'question_id').items():
        count = {}

        for i in headers:
            count[i] = sum([
                int(r[i])
                for r in q_list
            ])

        row = {
            'question_id': q,
            'question': q_list[0]['question'],
            'question_type': q_list[0]['question_type'],
            'question_group': q[:1]
        }
        for i, j in count.items():
            row[f"# {i}"] = j
            row[f"% {i}"] = f"{round(j / num_paper * 100)}%"

            cal_median[i].append(round(j / num_paper * 100))

        summary.append(row)

    for i, j in cal_median.items():
        print(f'Median {i}: {median(j)}')

    # TODO iqr

    dump_csv(table_path.parent / 'summarize_by_question.csv', summary)

    summarize_by_question_type(table_path.parent, summary)
    summarize_by_question_group(table_path.parent, summary)


def summarize_by_question_type(folder, summary):
    report = []
    for t, t_list in group_records_by(summary, 'question_type').items():

        headers = [
            i
            for i in t_list[0].keys()
            if i.startswith('#')
            ]

        total = len(t_list) * 60

        row = {
            'question_type': t
        }
        for h in headers:
            row[h] = sum([
                i[h]
                for i in t_list
            ])
            row[h.replace('#', '%')] = f"{row[h] / total * 100}%"

        report.append(row)

    dump_csv(folder / 'summarize_by_question_type.csv', report)


def summarize_by_question_group(folder, summary):
    report = []
    for t, t_list in group_records_by(summary, 'question_group').items():

        headers = [
            i
            for i in t_list[0].keys()
            if i.startswith('#')
            ]

        total = len(t_list) * 60

        row = {
            'question_group': t
        }
        for h in headers:
            row[h] = sum([
                i[h]
                for i in t_list
            ])
            row[h.replace('#', '%')] = f"{row[h] / total * 100}%"

        report.append(row)

    dump_csv(folder / 'summarize_by_question_group.csv', report)
