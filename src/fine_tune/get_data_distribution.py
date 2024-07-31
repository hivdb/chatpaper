from src.file_format import dump_csv
from src.excel2csv import load_excel
from src.preset import PAPER_PATH
from src.table import group_records_by
from collections import Counter


DATA_FILE = PAPER_PATH / 'Fine-tuning instruction set, Jul 31.xlsx'


def get_data_distribution():

    table = load_excel(DATA_FILE, 'Sheet1')

    result = []
    for qid, qid_list in group_records_by(table, 'QID').items():
        answers = [
            str(i['Answer']).lower()
            for i in qid_list
        ]

        for a, c in Counter(answers).items():
            result.append({
                'QID': qid,
                'answer': a,
                'Number': c
            })

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_report.csv')}"
    dump_csv(save_file, result)

    qids = sorted(list(set(
        int(i['QID'])
        for i in table
        )))

    result = []
    for pmid, pmid_list in group_records_by(table, 'PMID').items():
        paper = {
            'PMID': pmid
        }
        for i in qids:
            a = [
                r['Answer']
                for r in pmid_list
                if int(r['QID']) == i
            ]
            paper[str(i)] = a[0]

        result.append(paper)

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_pivot.csv')}"
    dump_csv(save_file, result, headers=['PMID'] + [str(i) for i in qids])


