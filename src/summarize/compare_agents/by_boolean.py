from src.table import group_records_by
from src.file_format import dump_csv
from src.statistics import calc_contigency_table
import matplotlib.pyplot as plt
import pandas as pd
import math
from itertools import permutations


def compare_boolean_questions(table, save_path):
    report = []

    for question_id, rows in group_records_by(table, 'question_id').items():

        question = rows[0]['question']
        question_id = rows[0]['question_id']

        human_answer = [
            (i['human_answer'], i['human_NA'])
            for i in rows
        ]

        AI_answer = [
            (i['AI_answer'], i['AI_NA'])
            for i in rows
        ]

        human_answer = [
            (
                1 if (
                    (i.lower() == 'yes') or
                    (i.lower().startswith('yes,'))
                ) else 0,
                1 if (
                    j.lower() == 'yes'
                ) else 0
            )
            for i, j in human_answer
        ]

        AI_answer = [
            (
                1 if (
                    (i.lower() == 'yes') or
                    (i.lower().startswith('yes,'))
                ) else 0,
                1 if (
                    j.lower() == 'yes'
                ) else 0
            )
            for i, j in AI_answer
        ]

        cont_table = get_triple_cont_table(human_answer, AI_answer)
        # spearman = calc_spearman(human_answer, AI_answer)

        # fisher = stats.fisher_exact([
        #     [cont_table['both'], cont_table['i_only']],
        #     [cont_table['j_only'], cont_table['none']]
        # ])

        true_positive = cont_table['H_Y_AI_Y']
        positive = sum([
            cont_table[f'H_{i}_AI_Y']
            for i in ['Y', 'N', 'NA']
        ])

        if positive > 0:
            ppv = f"{round(true_positive * 100 / positive, 2)}%"
        else:
            ppv = 'NA'

        row = {
            'question_id': question_id,
            'question': question,
        }
        row.update(cont_table)
        row['PPV'] = ppv

        # 'rho': spearman['spearman_rho'],
        # 'p vlaue': spearman['spearman_p_value'],
        # 'fisher': fisher.pvalue

        report.append(row)

    dump_csv(save_path, report)

    plot_ppv(save_path.parent / f'{save_path.stem}.PPV.png', report)

    if (save_path.parent / 'PPV.png').exists():
        (save_path.parent / 'PPV.png').unlink()


def plot_ppv(figure_path, table):

    table_data = [
        pd.DataFrame({
            i['question_id']: ['$Yes_{AI}$', '$No_{AI}$', '$NA_{AI}$'],
            '$Yes_{H}$': [i['H_Y_AI_Y'], i['H_Y_AI_N'], i['H_Y_AI_NA']],
            '$No_{H}$': [i['H_N_AI_Y'], i['H_N_AI_N'], i['H_N_AI_NA']],
            '$NA_{H}$': [i['H_NA_AI_Y'], i['H_NA_AI_N'], i['H_NA_AI_NA']],
        })
        for i in table
    ]
    ppv_data = [
        i['PPV']
        for i in table
    ]

    draw_ppv_table(figure_path, table_data, ppv_data)


def draw_ppv_table(figure_path, tables, ppv_values):

    fig, axes = plt.subplots(nrows=10, ncols=4, figsize=(24, 25))
    fig.subplots_adjust(hspace=0.5, wspace=0.3)

    axes_flat = axes.flatten()

    for ax in axes_flat:
        ax.axis('off')

    axes = axes.flatten()[:-2]

    for ax, table, ppv in zip(axes, tables, ppv_values):

        tbl = ax.table(
            cellText=table.values,
            colLabels=table.columns,
            loc='center',
            cellLoc='center')

        tbl.auto_set_font_size(False)
        tbl.set_fontsize(12)
        tbl.auto_set_column_width(col=list(range(len(table.columns))))

        cell_height = 0.3  # Adjust this value to your needs
        for key, cell in tbl.get_celld().items():
            cell.set_height(cell_height)

        # Display PPV to the right of the table
        ax.text(0.9, 0.5, f'PPV: {ppv}', transform=ax.transAxes, fontsize=10)

    plt.savefig(figure_path, dpi=300, bbox_inches='tight')


def get_triple_cont_table(human_answer, ai_answer):
    report = {}
    for i, j in permutations(['Y', 'N', 'NA'], 2):
        report[f"H_{i}_AI_{j}"] = 0
    for i in ['Y', 'N', 'NA']:
        report[f"H_{i}_AI_{i}"] = 0

    for (i1, i2), (j1, j2) in zip(human_answer, ai_answer):
        if i2 or j2:
            if i2 and j2:
                report['H_NA_AI_NA'] += 1
            if i2:
                if j1:
                    report['H_NA_AI_Y'] += 1
                else:
                    report['H_NA_AI_N'] += 1
            else:
                if i1:
                    report['H_Y_AI_NA'] += 1
                else:
                    report['H_N_AI_NA'] += 1
        else:
            if i1 and j1:
                report['H_Y_AI_Y'] += 1
            elif i1:
                report['H_Y_AI_N'] += 1
            elif j1:
                report['H_N_AI_Y'] += 1
            else:
                report['H_N_AI_N'] += 1

    return report
