from src.select_content.test_set import select_test_set
# from .option import select_report_date

from collections import defaultdict
from src.file_format import load_csv
from src.file_format import dump_csv
from src.excel2csv import excel2csv
from pathlib import Path

from .compare_agents.compare_agreement import compare_agreement
from .compare_agents.compare_human_ai import compare_human_and_ai
from .compare_agents.compare_ai_mode import compare_ai_mode_diff

from .ground_truth import summarize_ground_truth
from .basic_summarize import summarize_agreement
from .by_question import summarize_by_question
from .by_paper import summarize_by_paper
from .by_NA import check_NA_correct_rate

from .plot.by_question import plot_by_question
from .plot.by_paper import plot_by_paper

from .validate import validate
from src.table import group_records_by
from statistics import stdev
from statistics import quantiles
from statistics import mean, median
import re


def summarize():
    test_set_path_list = select_test_set(dialog='check_list')
    # model = select_model()

    # TODO: use chat mode to generate report
    # date = select_report_date(test_set_path)

    # TODO, select draw figure or not
    data_folder = merge_eval_files(test_set_path_list)

    analyze(data_folder)


def count_more_than_1_numbers(table):

    count = 0

    for i in table:
        if 'question_type' not in i:
            continue
        if i['question_type'] != 'Numerical':
            continue

        reply = i['AI_reply'].lower()

        ai_ans = re.findall(r'(\d+)', reply)
        if len(ai_ans) > 1:
            count += 1

    print(count)


def merge_eval_files(test_set_path_list):

    result = defaultdict(list)

    eval_files = []

    for i in test_set_path_list:
        for j in (i / 'evaluation').iterdir():
            if j.suffix == '.xlsx' and not j.name.startswith('~'):
                excel2csv(j, j.stem)

        for j in (i / 'evaluation').iterdir():
            if 'human_answer' in j.name:
                continue
            if j.suffix == '.csv':
                table = load_csv(j)
                result[j.name].extend(table)

                print(j)
                count_more_than_1_numbers(table)

                eval_files.append(j)

    validate(eval_files)

    folder = test_set_path_list[0].parent

    for name, d in result.items():
        dump_csv(folder / 'analysis' / name, d)

    return folder


def analyze(test_set_path):

    # summarize_eval(
    #     'GPT-4-multi_pair1', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
    #     ], rename_header={
    #         'gpt-4_base': 'gpt-4_base',
    #         'gpt-4_guide': 'gpt-4_instruction'
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ])

    # summarize_eval(
    #     'GPT-4-multi_pair2', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_2.csv'),
    #     ], rename_header={
    #         'gpt-4_base': 'gpt-4_base',
    #         'gpt-4_guide': 'gpt-4_instruction'
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ])

    # summarize_eval(
    #     'GPT-4-multi_pair3', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_3.csv'),
    #     ], rename_header={
    #         'gpt-4_base': 'gpt-4_base',
    #         'gpt-4_guide': 'gpt-4_instruction'
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ])

    # summarize_eval(
    #     'GPT-4-one', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_15.csv'),
    #     ], rename_header={
    #         'gpt-4_base_10': 'gpt-4_base',
    #         'gpt-4_guide_15': 'gpt-4_instruction'
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ])

    summarize_eval(
        'GPT-4-base_one_multi_1', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
        ], rename_header={
            'gpt-4_base_10': 'gpt-4_one_per_time',
            'gpt-4_base': 'gpt-4_all_per_time',
        }, colors=[
            '#1f78b4',
            '#ff7f00',
        ])

    summarize_eval(
        'GPT-4-base_one_multi_2', [
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_11.csv'),
        ], rename_header={
            'gpt-4_base_10': 'gpt-4_one_per_time',
            'gpt-4_base': 'gpt-4_all_per_time',
        }, colors=[
            '#1f78b4',
            '#ff7f00',
        ])

    summarize_eval(
        'GPT-4-base_one_multi_3', [
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_12.csv'),
        ], rename_header={
            'gpt-4_base_10': 'gpt-4_one_per_time',
            'gpt-4_base': 'gpt-4_all_per_time',
        }, colors=[
            '#1f78b4',
            '#ff7f00',
        ])

    # summarize_eval(
    #     'GPT-4-guide_one_multi', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_15.csv'),
    #     ], rename_header={
    #         'gpt-4_guide': 'gpt-4_all_per_time',
    #         'gpt-4_guide_15': 'gpt-4_one_per_time',
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ])

    # summarize_eval(
    #     'GPT-4-base_2', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
    #     ])

    # summarize_eval(
    #     'GPT-4-base_3', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
    #     ])

    summarize_eval(
        'GPT-4-base_3times_multi', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
        ], rename_header={
            'gpt-4_base': 'gpt-4_All Per Time, Run 1',
            'gpt-4_base_2': 'gpt-4_All Per Time, Run 2',
            'gpt-4_base_3': 'gpt-4_All Per time, Run 3',
        },
        additional_func=[get_stdev])

    # summarize_eval(
    #     'GPT-4-base_4times_multi', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_4.csv'),
    #     ], rename_header={
    #         'gpt-4_base': 'gpt-4_Run 1',
    #         'gpt-4_base_2': 'gpt-4_Run 2',
    #         'gpt-4_base_3': 'gpt-4_Run 3',
    #         'gpt-4_base_4': 'gpt-4_Run 4',
    #     },
    #     additional_func=[get_stdev])

    # summarize_eval(
    #     'GPT-4-guide_3times_multi', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_2.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_3.csv'),
    #     ], rename_header={
    #         'gpt-4_guide': 'gpt-4_All Per Time, Run 1',
    #         'gpt-4_guide_2': 'gpt-4_All Per Time, Run 2',
    #         'gpt-4_guide_3': 'gpt-4_All Per time, Run 3',
    #     },
    #     additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-3times_multi', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide_3.csv'),
        ], rename_header={
            'gpt-4_base': 'gpt-4_All Per Time, Run 1',
            'gpt-4_base_2': 'gpt-4_All Per Time, Run 2',
            'gpt-4_base_3': 'gpt-4_All Per time, Run 3',
        },
        bar_width=0.1,
        additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-3times_one_multi', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_11.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_12.csv'),
        ], rename_header={
            'gpt-4_base': 'gpt-4_All Per Time, Run 1',
            'gpt-4_base_2': 'gpt-4_All Per Time, Run 2',
            'gpt-4_base_3': 'gpt-4_All Per time, Run 3',
        },
        bar_width=0.1,
        additional_func=[get_stdev])

    # summarize_eval(
    #     'GPT-4-base_3times_one', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_11.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_12.csv'),
    #     ], rename_header={
    #         'gpt-4_base_10': 'gpt-4_One per time, Run 1',
    #         'gpt-4_base_11': 'gpt-4_One per time, Run 2',
    #         'gpt-4_base_12': 'gpt-4_One per time, Run 3',
    #     },
    #     additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-multi-Shuffle', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_1.csv'),
        ], rename_header={
            'gpt-4_base': 'gpt-4_base',
            'gpt-4_base_shuffle_paper': 'gpt-4_permutation',
        }, colors=[
            '#1f78b4',
            '#ff7f00',
        ]
    )

    # summarize_eval(
    #     'GPT-4-Shuffle', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_1.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_2.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_3.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_4.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_5.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_6.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_7.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_8.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_9.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper_10.csv'),
    #     ]
    # )

    # summarize_eval(
    #     'GPT-4-one-Shuffle', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
    #         Path(
    #             test_set_path / 'analysis' / 'gpt-4_base_10_shuffle_paper.csv'),
    #     ], rename_header={
    #         'gpt-4_base_10': 'gpt-4_base',
    #         'gpt-4_base_10_shuffle_paper': 'gpt-4_permutation',
    #     }, colors=[
    #         '#1f78b4',
    #         '#ff7f00',
    #     ]
    # )

    # summarize_eval(
    #     'GPT-4-1104', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_1104.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_1104.csv'),  # remove old text
    #     ])

    # summarize_eval(
    #     'GPT-4-2602', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_2602.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_2602.csv'),  # remove old text
    #     ])

    # summarize_eval(
    #     'GPT-4-6101', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_6101.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_6101.csv'),  # remove old text
    #     ])

    # summarize_eval(
    #     'GPT-4-6106', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_6106.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_6106.csv'),  # remove old text
    #     ])

    # summarize_eval(
    #     'GPT-4-2102', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2102.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2102.csv'),  # new question
    #     ])

    # summarize_eval(
    #     'GPT-4-2304', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_22304.csv'),  # old text
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_32304.csv'),  # new text
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_42304.csv'),  # new instruction
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_52304.csv'),  # new instruction 2
    #     ])

    # summarize_eval(
    #     'GPT-4-2605-2607', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_2605.csv'),   # new question
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_22605.csv'),   # new instruction new question
    #     ])

    # summarize_eval(
    #     'GPT-4-2605', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_32605.csv'),   # new instruction old question
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_42605.csv'),   # new text old question
    #     ])

    # summarize_eval(
    #     'GPT-4-4305-4306', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base_4305.csv'),  # new question
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_24305.csv'),  # new instruction new question
    #     ])

    # summarize_eval(
    #     'GPT-4-4305', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_34305.csv'),  # new instruction old question
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_44305.csv'),  # new text old question
    #     ])

    # summarize_eval(
    #     'GPT-4-2202', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_22202.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_22202.csv'),  # new instruction
    #         Path(test_set_path / 'analysis' / 'gpt-4_guide_32202.csv'),  # new text
    #     ])

    # summarize_eval(
    #     'GPT-4_vs_Claude', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'claude_base.csv'),
    #         Path(test_set_path / 'analysis' / 'claude_guide.csv'),
    #     ])

    # summarize_eval(
    #     'GPT-4_base_embed', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_embed.csv'),
    #     ])

    # summarize_eval(
    #     'GPT-4_embed', [
    #         Path(test_set_path / 'analysis' / 'gpt-4_embed.csv'),
    #         Path(test_set_path / 'analysis' / 'gpt-4_embed_guide.csv'),
    #     ])

    # eval_files = [
    #     Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #     Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
    #     Path(test_set_path / 'analysis' / 'claude_base.csv'),
    #     Path(test_set_path / 'analysis' / 'claude_guide.csv'),
    #     # Path(test_set_path / 'analysis' / 'gpt-4_embed.csv'),
    #     # Path(test_set_path / 'analysis' / 'gpt-4_embed_guide.csv'),
    # ]

    # compare_agreement(
    #     test_set_path / 'analysis' / 'compare_mode_agreement.csv',
    #     eval_files)

    # summarize_by_question(
    #     test_set_path / 'analysis' / 'compare_mode_agreement.csv')

    # summarize_by_paper(
    #     test_set_path / 'analysis' / 'compare_mode_agreement.csv')

    # compare_ai_mode_diff(
    #     test_set_path / 'analysis',
    #     eval_files)

    # check_NA_correct_rate(
    #     test_set_path / 'analysis' / 'check_NA_correct_rate.csv',
    #     eval_files
    # )

    # merge_disagree(test_set_path / 'analysis')


def get_stdev(summary_path):
    by_question_file = summary_path / 'summarize_by_question.csv'

    table = load_csv(by_question_file)

    headers = list(table[0].keys())
    headers = [
        i
        for i in headers
        if i.startswith('#')
    ]

    stdev_list = [
        stdev([
            int(i[j])
            for j in headers
        ])
        for i in table
    ]

    print('3times, iqr', quantiles(stdev_list))
    print('3times, range', max(stdev_list), min(stdev_list))
    print('3times, mean, median', mean(stdev_list), median(stdev_list))


def merge_disagree(folder):
    rows = []
    for i in folder.iterdir():
        if not i.is_dir():
            continue
        summary = i / 'summary' / 'mode_disagree_summary.csv'
        if not summary.exists():
            continue

        for j in load_csv(summary):
            for k in list(j.keys()):
                if k == 'question_id':
                    continue

                j[f"{k}_{i.name}"] = j[k]
                del j[k]

                rows.append(j)

    report = []
    for qid, qlist in group_records_by(rows, 'question_id').items():
        row = {
            'question_id': qid
        }
        for i in qlist:
            for k, v in i.items():
                if k == 'question_id':
                    continue
                row[k] = v

        report.append(row)

    dump_csv(folder / 'mode_disagree_summary.csv', report)


def summarize_eval(
        analysis_name, data_file_list, additional_func=[],
        rename_header={}, colors=None, bar_width=0.2):

    print(f'Work on {analysis_name}')

    summarize_ground_truth(data_file_list[0])

    save_path = data_file_list[0].parent / analysis_name
    save_path.mkdir(exist_ok=True, parents=True)

    summary_path = save_path / 'summary'
    summary_path.mkdir(exist_ok=True, parents=True)
    figure_path = save_path / 'figure'
    figure_path.mkdir(exist_ok=True, parents=True)

    compare_ai_mode_diff(
        summary_path,
        data_file_list)

    compare_file_path = summary_path / 'compare_agreement.csv'

    compare_agreement(
        compare_file_path, data_file_list)

    summarize_agreement(compare_file_path)
    summarize_by_question(compare_file_path)
    summarize_by_paper(compare_file_path)

    compare_human_and_ai(data_file_list, summary_path)

    if colors:
        plot_by_question(
            data_file_list, figure_path, rename_header=rename_header,
            figure_name='by_question.png', bar_width=bar_width, colors=colors)
    else:
        plot_by_question(
            data_file_list, figure_path, rename_header=rename_header,
            figure_name='by_question.png')

    plot_by_paper(
        data_file_list, figure_path,
        figure_name='by_paper.png')

    for i in additional_func:
        i(summary_path)
