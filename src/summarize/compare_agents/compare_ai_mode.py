from src.file_format import load_csv
from src.file_format import dump_csv
from collections import defaultdict
from operator import itemgetter
from src.table import group_records_by
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import matplotlib.patches as mpatches
from itertools import product
import numpy as np


def compare_ai_mode_diff(save_path, data_file_list):

    grouped = get_grouped_questions(data_file_list)
    report, improve, worse = get_disagree_with_human(grouped)

    dump_csv(save_path / 'disagree_with_human.csv', report)

    report_disagree = [
        i
        for i in report
        if i['same agree?'].lower() != 'yes'
    ]

    dump_csv(save_path / 'mode_disagree.csv', report_disagree)

    question_ids = list(set([
        i[1]
        for i in grouped.keys()
    ]))

    get_change_report(
        save_path / 'mode_disagree_summary.csv', grouped, question_ids)

    get_top_3_improve(save_path, improve)
    get_top_3_worse(save_path, worse)

    get_disagree_pattern(save_path / 'mode_disagree_pattern.csv', report)
    get_negative_pattern(save_path / 'mode_disagree_negative.csv', report)

    compare_pairs(data_file_list, save_path)


def compare_pairs(data_file_list, save_path):

    n_files = len(data_file_list)

    if n_files <= 2:
        return

    set1 = data_file_list[:(n_files // 2)]
    set2 = data_file_list[(n_files // 2):]

    save_path = save_path / 'pairs'
    save_path.mkdir(exist_ok=True, parents=True)

    reports = []

    for idx, (i, j) in enumerate(product(set1, set2)):

        grouped = get_grouped_questions([i, j])

        question_ids = list(set([
            i[1]
            for i in grouped.keys()
        ]))

        reports.append(get_change_report(
            save_path / f'{idx}.csv', grouped, question_ids))

    draw_compare(save_path / 'compare.png', reports)


def add_jitter(data, jitter_strength=0.1):
    jitter = jitter_strength * (np.random.rand(len(data)) - 0.5)
    return data + jitter


def draw_compare(save_path, reports):

    qid_group = defaultdict(list)
    for r in reports:
        for i in r:
            qid_group[i['question_id']].append(i)

    qid_group = list(qid_group.values())

    qid_group.sort(
        key=lambda x: [
            sum([
                i['# improve']
                for i in x
            ]),
            sum([
                i['# worse']
                for i in x
            ])
        ],
        reverse=True)

    group_labels = [
        f'Q{i[0]["question_id"]}'
        for i in qid_group
    ]

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))

    bar_positions = []
    bar_width = 0.2
    for pos, rows in enumerate(qid_group):
        bar_positions.append(pos)

        improves = [
            i['# improve'] / 60
            for i in rows
        ]

        q1, median, q3 = np.percentile(improves, [25, 50, 75])
        ax.scatter(
            add_jitter([pos] * len(improves)), improves, s=8, color='#1976D2')
        ax.hlines(
            [median], pos - 0.2, pos + 0.2,
            colors=['black'])

        ax.axhline(0, color='black', linewidth=0.5)

        worses = [
            i['# worse'] / -60
            for i in rows
        ]
        q1, median, q3 = np.percentile(worses, [25, 50, 75])
        ax.scatter(
            add_jitter([pos] * len(worses)), worses, s=8, color='#D32F2F')
        ax.hlines(
            [median], pos - 0.2, pos + 0.2,
            colors=['black'])

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_ylim(-0.2, 0.4)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def get_grouped_questions(data_file_list):
    date_tables = [
        load_csv(i)
        for i in data_file_list
    ]

    grouped = defaultdict(list)

    for table in date_tables:

        for row in table:
            grouped[(row['paper'], row['question_id'])].append(row)

    return grouped


def get_disagree_with_human(grouped):

    report = []
    improve = []
    worse = []
    for (paper, question_id), rows in grouped.items():

        agreement = [
            True if i['agree?'].lower().startswith('yes') else False
            for i in rows
        ]

        # if all(agreement):
        #     continue

        report_row = {
            'paper': paper,
            'question_id': question_id,
            'question': rows[0]['question'],
            'question_type': rows[0]['question_type'],
            'human_answer': rows[0]['human_answer'],
            # 'human_NA': rows[0]['human_NA'],
            'same agree?': 'Yes' if len(set(agreement)) == 1 else 'No'
        }

        for i in rows:
            report_row[f"{i['chat_mode']} AI_reply"] = i['AI_reply']
            report_row[f"{i['chat_mode']} AI_answer"] = i['AI_answer']
            # report_row[f"{i['chat_mode']} AI_NA"] = i['AI_NA']
            report_row[f"{i['chat_mode']} agree?"] = i['agree?']

        report.append(report_row)

        if len(agreement) != 2:
            continue

        if not agreement[0] and agreement[1]:
            improve.append(report_row)
        elif agreement[0] and not agreement[1]:
            worse.append(report_row)

    report.sort(key=itemgetter('question_id'))

    return report, improve, worse


def get_negative_pattern(save_path, report):

    table = []

    for qid, q_list in group_records_by(report, 'question_id').items():
        default = {
            'Boolean': 'No',
            'Categorical': 'NULL',
            'Numerical': '0'
        }
        question_type = q_list[0]['question_type']
        default = default[question_type]

        human_answer = [
            str(i['human_answer'])
            for i in q_list
        ]
        gt_negative = human_answer.count(default)

        q_gt_negative = [
            i
            for i in q_list
            if str(i['human_answer']) == default
        ]

        row = {
            'question_id': qid,
            'question_type': question_type,
            '# GT_negative': gt_negative,
            '% GT_negative': f"{gt_negative / 60 * 100}%",
        }

        if not q_gt_negative:
            table.append(row)
            continue

        AI_answer_keys = [
            i
            for i in q_gt_negative[0].keys()
            if 'agree?' in i
        ]

        AI_answers = {
            i: [
                j[i]
                for j in q_gt_negative
            ]
            for i in AI_answer_keys
        }

        for i, j in AI_answers.items():
            row[f"{i} agree"] = j.count('Yes')
            row[f"{i} not agree"] = len(j) - j.count('Yes')

        table.append(row)

    dump_csv(save_path, table)


def get_disagree_pattern(save_path, report):

    table = []
    for qid, q_list in group_records_by(report, 'question_id').items():
        question_type = q_list[0]['question_type']
        AI_answer_keys = [
            i
            for i in q_list[0].keys()
            if 'AI_answer' in i
        ]

        AI_answers = {
            i: [
                j[i]
                for j in q_list
            ]
            for i in AI_answer_keys
        }

        row = {
            'question_id': qid,
            'question_type': question_type
        }
        default = {
            'Boolean': 'No',
            'Categorical': 'NULL',
            'Numerical': '0'
        }
        default = default[question_type]
        for i, j in AI_answers.items():
            row[f"{i} is No/NULL/0"] = j.count(default)

        row['# disagree'] = len(q_list)

        table.append(row)

    dump_csv(save_path, table)


def get_change_report(save_path, grouped, question_ids):

    improve_count = defaultdict(int)
    worse_count = defaultdict(int)
    no_change = defaultdict(int)

    for (paper, question_id), rows in grouped.items():

        agreement = [
            True if i['agree?'].lower().startswith('yes') else False
            for i in rows
        ]

        if len(agreement) != 2:
            continue

        if agreement[0] and not agreement[1]:
            worse_count[question_id] += 1
        elif not agreement[0] and agreement[1]:
            improve_count[question_id] += 1
        elif agreement[0] and agreement[1]:
            no_change[question_id] += 1

    report = []
    for question_id in question_ids:
        row = {
            'question_id': question_id,
            '# no change': no_change.get(question_id, 0),
            '# improve': improve_count.get(question_id, 0),
            '# worse': worse_count.get(question_id, 0),
            '# diff': (
                improve_count.get(question_id, 0) -
                worse_count.get(question_id, 0))
        }
        row['# net change'] = row['# improve'] + row['# worse']

        report.append(row)

    dump_csv(save_path, report)
    plot_disagree(
        save_path.parent / save_path.name.replace('csv', 'png'), report)

    return report


def plot_disagree(save_path, report):

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))
    report.sort(key=lambda x: x['# no change'] + x['# worse'], reverse=True)

    group_labels = [
        f'Q{i["question_id"]}'
        for i in report
    ]

    bar_positions = []
    for pos, row in enumerate(report):
        bar_positions.append(pos)
        pos = pos - 0.2

        ax.bar(
            pos,
            (row['# no change'] + row['# worse']) / 60,
            width=0.2,
            color='#1261A0'
        )
        ax.bar(
            pos,
            - row['# worse'] / 60,
            width=0.2,
            color='#7B12A1',
        )

        pos += 0.2
        ax.bar(
            pos,
            (row['# no change'] + row['# improve']) / 60,
            width=0.2,
            color='#3895D3'
        )
        ax.bar(
            pos,
            - row['# improve'] / 60,
            width=0.2,
            color='#04D95C',
        )

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([0, 0.5, 1])
    ax.set_ylim(-0.5, 1.2)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


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
