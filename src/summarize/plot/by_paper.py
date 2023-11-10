import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
from collections import Counter
from collections import defaultdict
import string


COLORS = [
    '#1261A0',
    '#3895D3',
    '#58CCED',
    '#7ad6f0',

    '#963c32',
    '#ab625a',
    '#c08a84'
]


def detect_duplicate(names):
    counts = Counter(names)
    for name, count in counts:
        if count > 1:
            print(f'Find duplicates: {name}')

    return counts


def rename_paper(papers):

    new_names = defaultdict(list)

    for paper in papers:
        new_name = paper.split(',')[0].strip()
        new_names[new_name].append(paper)

    rename_map = {}

    for name, papers in new_names.items():
        if len(papers) == 1:
            rename_map[papers[0]] = name
            continue

        papers.sort()

        for idx, p in enumerate(papers):
            suffix = string.ascii_lowercase[idx]
            rename_map[p] = f"{name}{suffix}"

    return rename_map


def plot_by_paper(
        data_file_list,
        figure_path,
        figsize=(50, 10),
        figure_name='default.png',
        colors=COLORS):

    draw_context = {
        'figsize': figsize,
        'figure_path': (
            figure_path / figure_name)
    }

    draw_context['bar_width'] = 0.2

    data_file1 = data_file_list[0]
    df1 = pd.read_csv(data_file1)

    papers = df1[['paper']].drop_duplicates()

    renames = rename_paper(papers['paper'].tolist())

    papers['paper'] = papers['paper'].replace(renames)

    draw_context['papers'] = papers

    df_list = [
        pd.read_csv(i)
        for i in data_file_list
    ]

    for i in df_list:
        i['paper'] = i['paper'].replace(renames)

    df_list = [
        group_by_paper(i)
        for i in df_list
    ]

    df_list = [
        i.rename(columns={'agree?': j.stem})
        for i, j in zip(df_list, data_file_list)
    ]

    df = df_list[0]

    for i in df_list[1:]:
        df = df.merge(i, on='paper')

    header = list(df.head())

    df = df.sort_values(by=header, ascending=[False]*len(header))

    draw_context['df_grouped'] = df

    draw_context['colors'] = colors

    statistics = {}

    for i, (category, values) in enumerate(df.items()):
        statistics[category] = {
            'iqr25': round(values.quantile(0.25) * 100),
            'median': round(values.median() * 100),
            'iqr75': round(values.quantile(0.75) * 100),
            'max': round(max(values) * 100),
            'min': round(min(values) * 100)
        }

    draw_context['statistics'] = statistics

    draw_compare_plot(draw_context)


def group_by_paper(df):

    WANTED_COLUMNS = [
        'paper',
        "agree?",
    ]

    df = df[WANTED_COLUMNS]
    df = df.copy()

    df['agree?'] = df['agree?'].str.lower()
    df['agree?'] = df['agree?'].str.strip()
    df['agree?'] = df['agree?'].str.rstrip('?')
    df['agree?'] = df['agree?'].map({'yes': 1, 'no': 0})

    return df.groupby('paper').mean()


def draw_compare_plot(draw_context, split=False):
    df_grouped = draw_context['df_grouped']

    fig, ax = plt.subplots(1, 1, figsize=(25, 8))
    draw_compare_plot_with_legend(
        draw_context, df_grouped, ax, len(df_grouped), split=False)

    plt.savefig(draw_context['figure_path'], dpi=300, bbox_inches='tight')
    plt.close()


def draw_compare_plot_with_legend(
        draw_context, df_grouped, ax, max_label, split=True):

    # num_bars = len(df_grouped)
    num_groups = len(df_grouped.columns)
    # group_width = bar_width * num_groups

    group_labels = list(df_grouped.index)
    group_labels = [
        i
        for i in group_labels
    ]
    group_positions = np.array(range(1, len(group_labels) + 1))

    half = int(num_groups / 2)

    for i, (category, values) in enumerate(df_grouped.items()):
        pos = i - half

        bar_positions = group_positions + pos * draw_context['bar_width']

        bars = ax.bar(
            bar_positions,
            values.values,
            width=draw_context['bar_width'],
            color=draw_context['colors'][i],
            label=category)

        if i == 1:
            ax.set_xticks(bar_positions, group_labels)
            ax.set_xticklabels(group_labels, rotation=90)

        # for bar in bars:
        #     yval = bar.get_height()
        #     ax.text(
        #         bar.get_x() + bar.get_width() / 2,
        #         yval + 0.01,
        #         f"{round(yval * 100)}%",
        #         ha='center',
        #         va='bottom', fontsize=6)

    # ax.set_xlabel('paper ID')
    # ax.set_ylabel('Percentage of agreement')
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([0, 0.5, 1])
    ax.set_ylim(0, 1.2)

    if not split:
        handles, labels = plt.gca().get_legend_handles_labels()
        new_labels = {}
        for i in labels:
            stat = draw_context['statistics'][i]
            new_labels[i] = (
                f"{i[:-1] if i[-1] == '?' else i.replace('_', ' ').capitalize()}: "
                f"{stat['median']}% ({stat['iqr25']}%, {stat['iqr75']}%)")

        # ax.legend(handles, [new_labels.get(label, label) for label in labels])

    ax.margins(x=0.05)
    ax.set_xlim([0, max_label + 1])
