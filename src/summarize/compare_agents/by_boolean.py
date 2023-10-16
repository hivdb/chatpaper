from src.table import group_records_by
from src.file_format import dump_csv
from src.statistics import calc_contigency_table
import matplotlib.pyplot as plt
import pandas as pd
import math


def compare_boolean_questions(table, save_path):
    report = []

    for question_id, rows in group_records_by(table, 'question_id').items():

        question = rows[0]['question']
        question_id = rows[0]['question_id']

        human_answer = [
            i['human_answer']
            for i in rows
        ]

        AI_answer = [
            i['AI_answer']
            for i in rows
        ]

        human_answer = [
            (
                1 if (
                    (i.lower() == 'yes') or
                    (i.lower().startswith('yes,'))
                ) else 0
            )
            for i in human_answer
        ]

        AI_answer = [
            (
                1 if (
                    (i.lower() == 'yes') or
                    (i.lower().startswith('yes,'))
                ) else 0
            )
            for i in AI_answer
        ]

        cont_table = calc_contigency_table(human_answer, AI_answer)
        # spearman = calc_spearman(human_answer, AI_answer)

        # fisher = stats.fisher_exact([
        #     [cont_table['both'], cont_table['i_only']],
        #     [cont_table['j_only'], cont_table['none']]
        # ])

        if (cont_table['both'] + cont_table['j_only']) > 0:
            ppv = f"{round(cont_table['both'] * 100 / (cont_table['both'] + cont_table['j_only']), 2)}%"
        else:
            ppv = 'NA'

        report.append({
            'question_id': question_id,
            'question': question,
            'YY': cont_table['both'],
            'YN': cont_table['i_only'],
            'NY': cont_table['j_only'],
            'NN': cont_table['none'],
            'PPV': ppv,
            # 'rho': spearman['spearman_rho'],
            # 'p vlaue': spearman['spearman_p_value'],
            # 'fisher': fisher.pvalue
        })

    dump_csv(save_path, report)

    plot_ppv(save_path.parent / f'{save_path.stem}.PPV.png', report)

    if (save_path.parent / 'PPV.png').exists():
        (save_path.parent / 'PPV.png').unlink()


def plot_ppv(figure_path, table):

    table_data = [
        pd.DataFrame({
            i['question_id']: ['$Yes_{AI}$', '$No_{AI}$'],
            '$Yes_{H}$': [i['YY'], i['YN']],
            '$No_{H}$': [i['NY'], i['NN']],
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
        ax.text(0.7, 0.5, f'PPV: {ppv}', transform=ax.transAxes, fontsize=10)

    plt.savefig(figure_path, dpi=300, bbox_inches='tight')
