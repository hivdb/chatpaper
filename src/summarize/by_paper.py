from src.file_format import load_csv
from src.file_format import dump_csv
from src.table import group_records_by


def summarize_by_paper(table_path):
    table = load_csv(table_path)

    num_question = len(set(
        i['question_id']
        for i in table
    ))

    summary = []

    headers = list(table[0].keys())
    headers.remove('paper')
    headers.remove('question_id')
    headers.remove('question_type')
    headers.remove('question')
    headers.remove('# agree')

    for p, p_list in group_records_by(table, 'paper').items():

        counter = {}
        for i in headers:
            counter[i] = sum([
                int(r[i])
                for r in p_list
            ])

        row = {
            'paper': p,
        }

        for i, j in counter.items():
            row[f"# {i}"] = j
            row[f'% {i}'] = f"{round(j / num_question * 100)}%"

        summary.append(row)

    dump_csv(table_path.parent / 'summarize_by_paper.csv', summary)
