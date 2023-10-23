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


def summarize():
    test_set_path_list = select_test_set(dialog='check_list')
    # model = select_model()

    # TODO: use chat mode to generate report
    # date = select_report_date(test_set_path)

    # TODO, select draw figure or not
    data_folder = merge_eval_files(test_set_path_list)

    analyze(data_folder)


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
                result[j.name].extend(load_csv(j))

                eval_files.append(j)

    validate(eval_files)

    folder = test_set_path_list[0].parent

    for name, d in result.items():
        dump_csv(folder / 'analysis' / name, d)

    return folder


def analyze(test_set_path):

    summarize_eval(
        'GPT-4', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
        ])

    summarize_eval(
        'GPT-4-oneq', [
            Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide_15.csv'),
        ])

    summarize_eval(
        'GPT-4-base_2', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
        ])

    summarize_eval(
        'GPT-4-base_3', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
        ])

    summarize_eval(
        'GPT-4-base_3times', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
        ],
        additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-base_4times', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_4.csv'),
        ],
        additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-base_one_multi', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_2.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_3.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
        ],
        additional_func=[get_stdev])

    summarize_eval(
        'GPT-4-base_3times_one_per', [
            Path(test_set_path / 'analysis' / 'gpt-4_base_10.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_11.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_12.csv'),

        ],
        additional_func=[get_stdev])

    summarize_eval(
        'Shuffle', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_shuffle_paper.csv'),
        ]
    )

    summarize_eval(
        'GPT-4-extract', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_100.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide_101.csv'),
        ])

    summarize_eval(
        'GPT-4-RAG', [
            Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_base_200.csv'),
            Path(test_set_path / 'analysis' / 'gpt-4_guide_201.csv'),
        ])

    # summarize_eval(
    #     'Claude', [
    #         Path(test_set_path / 'analysis' / 'claude_base.csv'),
    #         Path(test_set_path / 'analysis' / 'claude_guide.csv'),
    #     ])

    # summarize_eval(
    #     'GPT-4_vs_Claude',
    #     [
    #         Path(test_set_path / 'analysis' / 'gpt-4_base.csv'),
    #         Path(test_set_path / 'analysis' / 'claude_base.csv'),
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


def summarize_eval(analysis_name, data_file_list, additional_func=[]):

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

    plot_by_question(
        data_file_list, figure_path,
        figure_name='by_question.png')

    plot_by_paper(
        data_file_list, figure_path,
        figure_name='by_paper.png')

    for i in additional_func:
        i(summary_path)

