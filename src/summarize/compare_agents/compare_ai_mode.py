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
import statistics


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
    compare_pairs2(data_file_list, save_path)

    draw_pairs(data_file_list, save_path / 'compareV200.png')


def compare_pairs(data_file_list, save_path):

    n_files = len(data_file_list)

    if n_files <= 2:
        return

    set1 = data_file_list[:(n_files // 2)]
    set2 = data_file_list[(n_files // 2):]

    save_path = save_path / 'pairs'
    save_path.mkdir(exist_ok=True, parents=True)

    reports = []

    for idx, (i, j) in enumerate(zip(set1, set2)):

        grouped = get_grouped_questions([i, j])

        question_ids = list(set([
            i[1]
            for i in grouped.keys()
        ]))

        reports.append(get_change_report(
            save_path / f'p{idx}.csv', grouped, question_ids))

    draw_compare(save_path / 'compare.png', reports)
    draw_compareV2(save_path / 'compareV2.png', reports)
    draw_compareV3(save_path / 'compareV3.png', reports)
    draw_compareV4(save_path / 'compareV4.png', reports)
    draw_compareV5(save_path / 'compareV5.png', reports)
    draw_compareV6(save_path / 'compareV6.png', reports)
    draw_compareV7(save_path / 'compareV7.png', reports)


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

        for idx, r in enumerate(rows):
            idx = idx - 1
            bar_pos = pos + idx * bar_width

            ax.bar(
                bar_pos,
                r['# improve'] / 60,
                width=bar_width,
                color='#1976D2',
                edgecolor='black',
                linewidth=1
            )

            ax.bar(
                bar_pos,
                r['# worse'] / -60,
                width=bar_width,
                color='#D32F2F',
                edgecolor='black',
                linewidth=1
            )

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_ylim(-0.2, 0.4)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV2(save_path, reports):

    qid_group = defaultdict(list)
    for r in reports:
        for i in r:
            qid_group[i['question_id']].append(i)

    qid_group = list(qid_group.values())

    qid_group.sort(
        key=lambda x: [
            statistics.median([
                i['# improve']
                for i in x
            ]),
            statistics.median([
                i['# worse']
                for i in x
            ]),
            statistics.median([
                i['# no change']
                for i in x
            ]),
        ],
        reverse=True)

    group_labels = [
        f'Q{i[0]["question_id"]}'
        for i in qid_group
    ]

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))

    bar_positions = []
    bar_width = 0.5

    for pos, rows in enumerate(qid_group):
        bar_positions.append(pos)

        improves = [
            i['# improve'] / 60
            for i in rows
        ]

        q1, median, q3 = np.percentile(improves, [25, 50, 75])
        q1, q3 = min(improves), max(improves)

        ax.bar(
            pos,
            median,
            width=bar_width,
            color='#1976D2',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos - 0.1, pos + 0.1,
        #     colors=['black'])
        # ax.vlines([pos], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos - 0.1, pos + 0.1,
        #     colors=['black'])

        worses = [
            i['# worse'] / -60
            for i in rows
        ]

        q1, median, q3 = np.percentile(worses, [25, 50, 75])
        q1, q3 = min(worses), max(worses)

        ax.bar(
            pos,
            median,
            width=bar_width,
            color='#D32F2F',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos - 0.1, pos + 0.1,
        #     colors=['black'])
        # ax.vlines([pos], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos - 0.1, pos + 0.1,
        #     colors=['black'])

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_ylim(-0.2, 0.4)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV3(save_path, reports):

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
    bar_width = 0.5

    for pos, rows in enumerate(qid_group):
        bar_positions.append(pos)

        changes = [
            (i['# improve'] - i['# worse']) / 60
            for i in rows
        ]

        q1, median, q3 = np.percentile(changes, [25, 50, 75])
        q1, q3 = min(changes), max(changes)

        ax.bar(
            pos,
            median,
            width=bar_width,
            color='#1976D2' if median >= 0 else '#D32F2F',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos - 0.1, pos + 0.1,
        #     colors=['black'])
        # ax.vlines([pos], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos - 0.1, pos + 0.1,
        #     colors=['black'])

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_ylim(-0.2, 0.4)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV4(save_path, reports):

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

        for idx, r in enumerate(rows):
            idx = idx - 1
            bar_pos = pos + idx * bar_width

            change = (r['# improve'] - r['# worse']) / 60

            ax.bar(
                bar_pos,
                change,
                width=bar_width,
                color='#1976D2' if change >= 0 else '#D32F2F',
                edgecolor='black',
                linewidth=1
            )

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_ylim(-0.2, 0.4)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV5(save_path, reports):

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

        for idx, r in enumerate(rows):
            idx = idx - 1
            bar_pos = pos + idx * bar_width

            no_change = r['# no change'] / 60
            ax.bar(
                bar_pos,
                no_change,
                width=bar_width,
                color='#828282',
                edgecolor='black',
                linewidth=1
            )

            change = (r['# improve'] - r['# worse']) / 60

            ax.bar(
                bar_pos,
                change,
                bottom=no_change,
                width=bar_width,
                color='#1976D2' if change >= 0 else '#D32F2F',
                edgecolor='black',
                linewidth=1
            )

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([0, 0.5, 1])
    ax.set_ylim(0, 1.2)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV6(save_path, reports):

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

        for idx, r in enumerate(rows):
            idx = idx - 1
            bar_pos = pos + idx * bar_width

            no_change = r['# no change'] / 60

            ax.bar(
                bar_pos,
                no_change,
                width=bar_width,
                color='#828282',
                edgecolor='black',
                linewidth=1
            )

            improve = r['# improve'] / 60

            ax.bar(
                bar_pos,
                improve,
                bottom=no_change,
                width=bar_width,
                color='#1976D2',
                edgecolor='black',
                linewidth=1
            )

            worse = r['# worse'] / -60

            ax.bar(
                bar_pos,
                worse,
                width=bar_width,
                color='#D32F2F',
                edgecolor='black',
                linewidth=1
            )

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([-0.2, 0.5, 1])
    ax.set_ylim(-0.2, 1.2)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')

    # ax.legend(handles=[legend_handle1, legend_handle2])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def draw_compareV7(save_path, reports):

    qid_group = defaultdict(list)
    for r in reports:
        for i in r:
            qid_group[i['question_id']].append(i)

    qid_group = list(qid_group.values())

    qid_group.sort(
        key=lambda x: [
            statistics.median([
                i['# improve']
                for i in x
            ]),
            statistics.median([
                i['# worse']
                for i in x
            ]),
            statistics.median([
                i['# no change']
                for i in x
            ]),
        ],
        reverse=True)

    group_labels = [
        f'Q{i[0]["question_id"]}'
        for i in qid_group
    ]

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))

    bar_positions = []
    bar_width = 0.6

    for pos, rows in enumerate(qid_group):
        bar_positions.append(pos)

        no_change = [
            i['# no change'] / 60
            for i in rows
        ]
        q1, median, q3 = np.percentile(no_change, [25, 50, 75])
        q1, q3 = min(no_change), max(no_change)
        ax.bar(
            pos,
            median,
            width=bar_width,
            color='#828282',
            # edgecolor='black',
            # linewidth=1
        )

        bottom = median

        worses = [
            i['# worse'] / 60
            for i in rows
        ]

        q1, median, q3 = np.percentile(worses, [25, 50, 75])
        q1, q3 = min(worses), max(worses)

        pos -= bar_width / 2 / 2
        q1 += bottom
        q3 += bottom

        ax.bar(
            pos,
            median,
            bottom=bottom,
            width=bar_width / 2,
            color='#D32F2F',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos - 0.1, pos + 0.1,
        #     colors=['black'])
        # ax.vlines([pos], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos - 0.1, pos + 0.1,
        #     colors=['black'])

        improves = [
            i['# improve'] / 60
            for i in rows
        ]

        q1, median, q3 = np.percentile(improves, [25, 50, 75])
        q1, q3 = min(improves), max(improves)

        pos += bar_width / 2
        q1 = q1 + bottom
        q3 = q3 + bottom

        ax.bar(
            pos,
            median,
            bottom=bottom,
            width=bar_width / 2,
            color='#1976D2',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos - 0.1, pos + 0.1,
        #     colors=['black'])
        # ax.vlines([pos], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos - 0.1, pos + 0.1,
        #     colors=['black'])

    ax.axhline(0, color='black', linewidth=0.5)

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks(np.arange(0, 11, 2) / 10)
    ax.set_ylim(0, 1.1)
    ax.tick_params(axis='y', labelsize=14)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    legend_handle1 = mpatches.Patch(color='#1976D2', label='Improved')
    legend_handle2 = mpatches.Patch(color='#D32F2F', label='Worsen')
    legend_handle3 = mpatches.Patch(color='#828282', label='Correct in both')

    # ax.legend(handles=[legend_handle1, legend_handle2, legend_handle3])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def compare_pairs2(data_file_list, save_path):

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

    draw_compare2(save_path / 'compareV100.png', reports)


def add_jitter(data, jitter_strength=0.1):
    jitter = jitter_strength * (np.random.rand(len(data)) - 0.5)
    return data + jitter


def draw_compare2(save_path, reports):

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
        q1, q3 = min(improves), max(improves)

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
        q1, q3 = min(worses), max(worses)

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

    # ax.legend(handles=[legend_handle1, legend_handle2])

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
            '# net change': (
                improve_count.get(question_id, 0) -
                worse_count.get(question_id, 0))
        }
        row['# total change'] = row['# improve'] + row['# worse']

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


def draw_pairs(data_file_list, save_path):

    n_files = len(data_file_list)

    if n_files <= 2 or (n_files % 2 != 0):
        return

    set1 = data_file_list[:(n_files // 2)]
    set2 = data_file_list[(n_files // 2):]

    set1_group = defaultdict(list)

    for f in set1:
        for qid, rows in group_records_by(load_csv(f), 'question_id').items():
            agreement = [
                i
                for i in rows
                if i['agree?'].lower().startswith('yes')
            ]
            set1_group[qid].append(len(agreement))

    set2_group = defaultdict(list)

    for f in set2:
        for qid, rows in group_records_by(load_csv(f), 'question_id').items():
            agreement = [
                i
                for i in rows
                if i['agree?'].lower().startswith('yes')
            ]
            set2_group[qid].append(len(agreement))

    qid_group = []
    for qid, multi in set1_group.items():
        qid_group.append({
            'question_id': qid,
            'group1': multi,
            'group2': set2_group[qid],
            'median_group1': statistics.median(multi),
            'median_group2': statistics.median(set2_group[qid]),
            'delta': statistics.median(multi) - statistics.median(set2_group[qid])
        })

    qid_group.sort(
        key=lambda x: x['delta'],
        reverse=True)

    group_labels = [
        f'Q{i["question_id"]}'
        for i in qid_group
    ]

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))

    bar_positions = []
    bar_width = 0.6

    prev_delta = None

    for pos, row in enumerate(qid_group):
        bar_positions.append(pos)

        group1_accuracy = [
            i / 60
            for i in row['group1']
        ]
        q1, median, q3 = np.percentile(group1_accuracy, [25, 50, 75])
        q1, q3 = min(group1_accuracy), max(group1_accuracy)
        pos1 = pos - bar_width / 2 / 2
        ax.bar(
            pos1,
            median,
            width=bar_width / 2,
            color='#1f78b4',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos1 - 0.1, pos1 + 0.1,
        #     colors=['black'])
        # ax.vlines([pos1], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos1 - 0.1, pos1 + 0.1,
        #     colors=['black'])

        group2_accuracy = [
            i / 60
            for i in row['group2']
        ]

        q1, median, q3 = np.percentile(group2_accuracy, [25, 50, 75])
        q1, q3 = min(group2_accuracy), max(group2_accuracy)

        pos2 = pos + bar_width / 2 / 2

        ax.bar(
            pos2,
            median,
            width=bar_width / 2,
            color='#ff7f00',
            # edgecolor='black',
            # linewidth=1
        )
        # ax.hlines(
        #     [q1], pos2 - 0.1, pos2 + 0.1,
        #     colors=['black'])
        # ax.vlines([pos2], q1, q3, colors=['black'])
        # ax.hlines(
        #     [q3], pos2 - 0.1, pos2 + 0.1,
        #     colors=['black'])

        delta = abs(row['delta'])

        if not prev_delta:
            prev_delta = delta
            continue

        if delta >= 6 and prev_delta < 6:
            ax.axvline(x=pos - 0.5, color='grey', linestyle='--')
        elif delta < 6 and prev_delta >= 6:
            ax.axvline(x=pos - 0.5, color='grey', linestyle='--')

        prev_delta = delta

    ax.set_xticks(bar_positions, group_labels)
    ax.set_xticklabels(group_labels, rotation=90)

    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks(np.arange(0, 11, 2) / 10)
    ax.set_ylim(0, 1.1)
    ax.tick_params(axis='y', labelsize=14)

    ax.margins(x=0.05)
    ax.set_xlim([-1, 60])

    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
