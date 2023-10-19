import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np


# TODO, selection which to draw, and which file to draw


def plot_by_question(
        data_file_list,
        figure_path,
        figsize=(50, 10),
        figure_name='default.png'):

    draw_context = {
        'figsize': figsize,
        'figure_path': (
            figure_path / figure_name)
    }

    draw_context['bar_width'] = 0.2

    data_file1 = data_file_list[0]
    df1 = pd.read_csv(data_file1)

    questions = df1[['question_id', 'question']].drop_duplicates()

    questions['question'] = questions.apply(
        lambda row: f"{row['question_id']}. {row['question']}", axis=1)

    draw_context['questions'] = questions

    df_list = [
        group_by_question_id(pd.read_csv(i))
        for i in data_file_list
    ]

    df_list = [
        i.rename(columns={'agree?': j.stem})
        for i, j in zip(df_list, data_file_list)
    ]

    # Get the column headers
    df = df_list[0]

    for i in df_list[1:]:
        df = df.merge(i, on=['question_id', 'question_type'])
    header = list(df.head())
    # assert (len(header) == 3)

    df.reset_index(inplace=True)
    df_grouped = df.sort_values(by=header, ascending=[False]*len(header))
    del df_grouped['question_type']
    df_grouped.set_index('question_id', inplace=True)
    draw_context['df_grouped'] = df_grouped

    df_typed = {name: group for name, group in df.groupby('question_type')}
    for name in df_typed.keys():
        d = df_typed[name]
        del d['question_type']
        d.set_index('question_id', inplace=True)
        header1 = header[0]
        header2 = header[1]
        d['diff'] = d[header1] - d[header2]
        d = d.sort_values(
            by=['diff'], ascending=[False])
        d.drop('diff', axis=1, inplace=True)
        df_typed[name] = d

    draw_context['df_grouped_by_type'] = df_typed

    COLORS = [
        # '#072F5F',
        '#1261A0',
        '#3895D3',
        '#58CCED',
        '#7ad6f0',
        '#7ad6f0',
    ]

    draw_context['colors'] = COLORS

    statistics = {}

    for i, (category, values) in enumerate(df_grouped.items()):
        statistics[category] = {
            'iqr25': round(values.quantile(0.25) * 100),
            'median': round(values.median() * 100),
            'iqr75': round(values.quantile(0.75) * 100),
            'max': round(max(values) * 100),
            'min': round(min(values) * 100)
        }

    draw_context['statistics'] = statistics

    draw_compare_plot(draw_context)

    draw_context['figure_path'] = (
        figure_path / 'grouped_question.png')
    draw_compare_plot(draw_context, split=True)

    draw_context['figure_path'] = (
        figure_path / 'typed_question.png')
    draw_compare_plot(draw_context, question_type=True)

    # draw_context['df_grouped'] = df.sort_values(
    #     by=['question_id'], ascending=[True])
    # draw_context['figure_path'] = (
    #     figure_path / 'ordered_question.png')
    # draw_compare_plot(draw_context)

    header1 = header[0]
    header2 = header[1]
    df_grouped['diff'] = df_grouped[header1] - df_grouped[header2]
    df_grouped = df_grouped.sort_values(
        by=['diff'], ascending=[False])
    df_grouped.drop('diff', axis=1, inplace=True)
    draw_context['df_grouped'] = df_grouped
    draw_context['figure_path'] = (
        figure_path / 'ordered_diff.png')
    draw_compare_plot(draw_context)


def group_by_question_id(df):

    WANTED_COLUMNS = [
        'question_id',
        "agree?",
        'question_type',
    ]

    df = df[WANTED_COLUMNS]
    df = df.copy()

    df['agree?'] = df['agree?'].str.lower()
    df['agree?'] = df['agree?'].str.strip()
    df['agree?'] = df['agree?'].str.rstrip('?')
    df['agree?'] = df['agree?'].map({'yes': 1, 'no': 0})

    return df.groupby(['question_id', 'question_type']).mean()


def draw_compare_plot(draw_context, split=False, question_type=False):
    df_grouped = draw_context['df_grouped']

    if split:
        fig, axes = plt.subplots(7, 1, figsize=(20, 35))
        groups = get_df_group_list(df_grouped)

        max_label = max(len(i) for i in groups)
        for idx, df in enumerate(get_df_group_list(df_grouped)):
            draw_compare_plot_with_legend(
                draw_context, df, axes[idx], max_label, split=True)
        fig.subplots_adjust(hspace=0.5)
        # axes[3, 1].remove()

    elif question_type:
        fig, axes = plt.subplots(3, 1, figsize=(20, 20))
        df_grouped = draw_context['df_grouped_by_type']
        # groups = get_df_group_by_type(df_grouped)

        max_label = 38
        for idx, (name, df) in enumerate(df_grouped.items()):
            draw_compare_plot_with_legend(
                draw_context, df, axes[idx], max_label, split=True,
                figure_name=name)
        fig.subplots_adjust(hspace=0.5)
    else:
        fig, ax = plt.subplots(1, 1, figsize=(25, 8))
        draw_compare_plot_with_legend(
            draw_context, df_grouped, ax, len(df_grouped), split=False)

        # text = '\n'.join(draw_context['questions']['question'])
        # plt.figtext(
        #     0.2, -0.1, text,
        #     transform=plt.gcf().transFigure,
        #     fontsize=7, va='center', ha='left',
        #     bbox=dict(facecolor='white', edgecolor='black'))

    plt.savefig(draw_context['figure_path'], dpi=300, bbox_inches='tight')


def draw_compare_plot_with_legend(
        draw_context, df_grouped, ax, max_label, split=True, figure_name=None):

    # num_bars = len(df_grouped)
    num_groups = len(df_grouped.columns)
    # group_width = bar_width * num_groups

    group_labels = list(df_grouped.index)
    group_labels = [
        f'Q{i}'
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

    # ax.set_xlabel('Question ID')
    # ax.set_ylabel('Percentage of agreement')
    ax.yaxis.set_major_formatter(PercentFormatter(1))

    ax.set_yticks([0, 0.5, 1])
    ax.set_ylim(0, 1.2)

    # if not split:
    handles, labels = plt.gca().get_legend_handles_labels()
    new_labels = {}
    for i in labels:
        # stat = draw_context['statistics'][i]
        new_labels[i] = (
            f"{i[:-1] if i[-1] == '?' else i.replace('_', ' ').upper()}"
            #: f"{stat['median']}% ({stat['iqr25']}%, {stat['iqr75']}%)"
            )

    ax.legend(handles, [new_labels.get(label, label) for label in labels])

    ax.margins(x=0.05)
    ax.set_xlim([0, max_label + 1])

    if figure_name:
        ax.text(
            0.95, 1.05, figure_name,
            transform=ax.transAxes, ha='right', va='bottom', fontsize=12)


def get_df_group_list(df_grouped):
    result = []
    df = df_grouped.reset_index()
    df['question_id'] = df['question_id'].astype('str')
    q_groups = sorted(list(set([
        i[0]
        for i in df['question_id']
    ])))
    for q in q_groups:
        new_df = df[df['question_id'].str.startswith(q)]
        new_df.set_index('question_id', inplace=True)
        result.append(new_df)

    return result
