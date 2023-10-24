import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import numpy as np
from src.file_format import load_csv

pd.options.mode.chained_assignment = None


# TODO, selection which to draw, and which file to draw

# COLORS = [
#     # '#072F5F',
#     '#1261A0',
#     '#3895D3',
#     '#58CCED',
#     '#7ad6f0',
# ]

COLORS = [
    '#1261A0',
    '#3895D3',
    '#58CCED',
    '#7ad6f0',

    '#963c32',
    '#ab625a',
    '#c08a84'
]


def plot_by_question(
        data_file_list,
        figure_path,
        figsize=(50, 10),
        rename_header={},
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

    if rename_header:
        df_list = [
            i.rename(columns=rename_header)
            for i in df_list
        ]

    # Get the column headers
    df = df_list[0]

    for i in df_list[1:]:
        df = df.merge(i, on=['question_id', 'question_type'])
    header = list(df.head())
    # assert (len(header) == 3)

    df.reset_index(inplace=True)
    # df['question_type'] = df['question_type'].replace({
    #     'Categorical': 'List',
    #     'Numerical': 'Number',
    # })
    df.set_index(['question_id', 'question_type'], inplace=True)

    df.reset_index(inplace=True)
    df_grouped = df.sort_values(by=header, ascending=[False]*len(header))
    del df_grouped['question_type']
    df_grouped.set_index('question_id', inplace=True)
    draw_context['df_grouped'] = df_grouped

    draw_context['df_grouped_by_type'] = get_grouped_by_reason(
        df, data_file_list, header)

    draw_context['colors'] = colors

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
        figure_path / 'reasoned_question.png')
    draw_compare_plot(draw_context, question_type=True)

    draw_context['df_grouped_by_type'] = get_grouped_by_type(
        df, header)
    draw_context['figure_path'] = (
        figure_path / 'typed_question.png')
    draw_compare_plot(draw_context, question_type=True)

    draw_context['df_grouped_by_type'] = get_grouped_by_diff(
        df, header)
    draw_context['figure_path'] = (
        figure_path / 'diff_question.png')
    draw_compare_plot(draw_context, question_type=True)

    df_default = get_grouped_by_default(
        df, figure_path, header)
    if df_default:
        draw_context['df_grouped_by_type'] = df_default
        draw_context['figure_path'] = (
            figure_path / 'default_question.png')
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


def get_grouped_by_default(df, figure_path, header):
    disagree_pattern = figure_path.parent / 'summary' / 'mode_disagree_pattern.csv'
    disagree_pattern = load_csv(disagree_pattern)

    columns = [
        i
        for i in disagree_pattern[0].keys()
        if i not in ('question_id', 'question_type', '# disagree')
    ]

    if len(columns) != 2:
        return None

    c1, c2 = columns

    disagree_qid = [
        int(i['question_id'])
        for i in disagree_pattern
        if (
            int(i[c1]) >= 10 and int(i[c2]) <= 1
        ) or (
            int(i[c2]) >= 10 and int(i[c1]) <= 1
        )
    ]

    grouped = get_grouped_by_diff(df, header)

    grouped_by_default = []
    for name, df in grouped:
        grouped_by_default.append([
            name,
            df[df['question_id'].isin(disagree_qid)]
        ])
        grouped_by_default.append([
            name,
            df[~df['question_id'].isin(disagree_qid)]
        ])

    return grouped_by_default


def get_grouped_by_diff(df, header):

    header1 = header[0]
    header2 = header[1]
    df = df[['question_id', header1, header2]]
    df['diff'] = df[header1] - df[header2]
    df = df.sort_values(
        by=['diff'], ascending=[False])

    sub1 = df[df['diff'] < -0.02]
    sub2 = df[(df['diff'] >= -0.02) & (df['diff'] <= 0.02)]
    sub3 = df[df['diff'] >= 0.02]

    sub1.drop('diff', axis=1, inplace=True)
    sub2.drop('diff', axis=1, inplace=True)
    sub3.drop('diff', axis=1, inplace=True)

    grouped = [
        ('', sub3),
        ('', sub2),
        ('', sub1),
    ]

    return grouped


def get_grouped_by_type(df, header):

    df = {name: group for name, group in df.groupby('question_type')}

    typed = []
    for name in ['Boolean', 'Numerical', 'Categorical']:
        if name not in df:
            continue

        df_sub = df[name]

        header1 = header[0]
        header2 = header[1]
        df_sub = df_sub[['question_id', header1, header2]]

        df_sub['diff'] = df_sub[header1] - df_sub[header2]

        df_sub = df_sub.sort_values(
                by=['diff'], ascending=[False])
        df_sub.drop('diff', axis=1, inplace=True)

        typed.append((name, df_sub))

    return typed


def get_grouped_by_reason(df, data_file_paths, header):

    gt_path = data_file_paths[0].parent / 'summarize_ground_truth.csv'
    ground_truth = pd.read_csv(gt_path)

    df = df.merge(ground_truth, on=['question_id', 'question_type'])

    df = {name: group for name, group in df.groupby('question_type')}

    df_typed = []

    for name in ['Boolean', 'Numerical', 'Categorical']:
        if name not in df:
            continue
        df_sub = df[name]
        if name == 'Boolean':
            df_sub = df_sub[
                ['question_id', header[0], header[1], '# GT_Yes']]

            header1 = header[0]
            header2 = header[1]
            df_sub['diff'] = df_sub[header1] - df_sub[header2]

            df_sub1 = df_sub[df_sub[header1] <= 0.75]
            df_sub = df_sub[df_sub[header1] > 0.75]

            df_sub1 = df_sub1.sort_values(
                by=['diff'], ascending=[False])
            df_sub1.drop('diff', axis=1, inplace=True)
            df_sub1.drop('# GT_Yes', axis=1, inplace=True)

            # df_sub2 = df_sub[
            #     (df_sub['# GT_Yes'] >= 4) & (df_sub['# GT_Yes'] <= 56)]

            df_sub2 = df_sub[(df_sub['diff'] > 0.1)]

            df_sub2 = df_sub2.sort_values(
                by=['diff'], ascending=[False])
            df_sub2.drop('diff', axis=1, inplace=True)
            df_sub2.drop('# GT_Yes', axis=1, inplace=True)

            # df_sub3 = df_sub[
            #     (df_sub['# GT_Yes'] < 4) | (df_sub['# GT_Yes'] > 56)]

            df_sub3 = df_sub[(df_sub['diff'] <= 0.1)]

            df_sub3 = df_sub3.sort_values(
                by=['diff'], ascending=[False])
            df_sub3.drop('diff', axis=1, inplace=True)
            df_sub3.drop('# GT_Yes', axis=1, inplace=True)

            df_typed.append((name, df_sub2))
            df_typed.append((name, df_sub3))
            df_typed.append((name, df_sub1))

        else:
            df_sub = df_sub[
                ['question_id', header[0], header[1], '# same']]

            header1 = header[0]
            header2 = header[1]
            df_sub['diff'] = df_sub[header1] - df_sub[header2]

            df_sub1 = df_sub[df_sub['# same'] < 8]
            df_sub2 = df_sub[df_sub['# same'] >= 8]

            df_sub1 = df_sub1.sort_values(
                by=['diff'], ascending=[False])
            df_sub1.drop('diff', axis=1, inplace=True)
            df_sub1.drop('# same', axis=1, inplace=True)

            df_sub2 = df_sub2.sort_values(
                by=['diff'], ascending=[False])
            df_sub2.drop('diff', axis=1, inplace=True)
            df_sub2.drop('# same', axis=1, inplace=True)

            df_typed.append((name, df_sub2))
            df_typed.append((name, df_sub1))

    return df_typed


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
        fig, ax = plt.subplots(1, 1, figsize=(25, 8))
        df_typed = draw_context['df_grouped_by_type']
        df_grouped = []
        plot_num = []

        line_pos = 0
        for name, df in df_typed:
            df_grouped.append(df)
            num_items = len(df)
            plot_num.append((
                # name,
                '',
                num_items + line_pos,
                line_pos + num_items // 2))
            line_pos = num_items + line_pos

        plot_num.pop(-1)

        df_grouped = pd.concat(df_grouped)
        df_grouped.set_index('question_id', inplace=True)

        draw_compare_plot_with_legend(
            draw_context, df_grouped, ax, len(df_grouped), split=False,
            plot_line=plot_num
            )
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
    plt.close()


def draw_compare_plot_with_legend(
        draw_context, df_grouped, ax, max_label,
        split=True, plot_line={}):

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

    for name, pos, text_pos in plot_line:
        ax.axvline(x=pos + 0.5, color='grey', linestyle='--')
        plt.text(
            text_pos, 1.1,
            name,
            ha='center', va='bottom')

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
        stat = draw_context['statistics'][i]
        new_labels[i] = (
            f"{i[:-1] if i[-1] == '?' else i.replace('_', ' ').upper()}"
            f": {stat['median']}% ({stat['iqr25']}%, {stat['iqr75']}%)"
            )

    ax.legend(handles, [new_labels.get(label, label) for label in labels])

    ax.margins(x=0.05)
    ax.set_xlim([0, max_label + 1])


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
