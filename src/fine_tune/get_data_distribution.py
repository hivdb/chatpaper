from src.file_format import dump_csv
from src.excel2csv import load_excel
from src.preset import PAPER_PATH
from src.table import group_records_by
from collections import Counter
from sklearn.model_selection import train_test_split
import pandas as pd


DATA_FILE = PAPER_PATH / 'Fine-tuning instruction set, Step 4.xlsx'
# DATA_FILE = PAPER_PATH / 'Testset_Aug23.xlsx'


def get_data_distribution():

    table = load_excel(DATA_FILE, 'Sheet1')

    result = []
    result2 = []
    for qid, qid_list in group_records_by(table, 'QID').items():
        answers = [
            str(i['Answer']).strip()
            for i in qid_list
        ]

        for a, c in Counter(answers).items():
            result.append({
                'QID': qid,
                'answer': a,
                'Number': c
            })
        # if int(qid) == 11:
        #     for j in sorted(answers):
        #         print(j)
        if int(qid) not in (3, 6, 7, 18):
            answers = [
                sub_a.strip()
                for a in answers
                for sub_a in (
                    a.split(',') if (',' in a) else a.split(';')
                )
            ]

        for a, c in Counter(answers).items():
            result2.append({
                'QID': qid,
                'answer': a,
                'Number': c
            })

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_report.csv')}"
    dump_csv(save_file, result)

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_report2.csv')}"
    dump_csv(save_file, result2)

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
                str(r['Answer']).strip()
                for r in pmid_list
                if int(r['QID']) == i
            ]
            paper[str(i)] = a[0]

        result.append(paper)

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_pivot.csv')}"
    dump_csv(save_file, result, headers=['PMID'] + [str(i) for i in qids])

    for row in result:
        for k in row.keys():
            if k == 'PMID':
                continue
            if str(row[k]).strip() in ['No', 'Not reported', 'None']:
                row[k] = 'No'
            if 'HIV-2' in str(row[k]):
                row[k] = 'No'
            else:
                row[k] = 'Yes'

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_pivot_stratify.csv')}"
    dump_csv(save_file, result, headers=['PMID'] + [str(i) for i in qids])

    for row in result:
        row['combined'] = '_'.join([
            str(row[k])
            for k in row.keys()
            if str(k) in ['1', '2', '3', '8', '11', '14', '16', '19']
        ])

    df = pd.DataFrame(result)

    train, val = train_test_split(
        df, train_size=0.8, stratify=df['combined'],
        random_state=42)

    # val, test = train_test_split(
    #     val_test, test_size=0.5, stratify=val_test['combined'],
    #     random_state=42)

    # test = []

    split_paper = []
    for i in train["PMID"].tolist():
        split_paper.append({
            'PMID': i,
            'category': 'train'
        })

    for i in val["PMID"].tolist():
        split_paper.append({
            'PMID': i,
            'category': 'val'
        })

    # for i in test["PMID"].tolist():
    #     split_paper.append({
    #         'PMID': i,
    #         'category': 'test'
    #     })

    save_file = DATA_FILE.parent / f"{DATA_FILE.name.replace('.xlsx', '_split.csv')}"
    dump_csv(save_file, split_paper)
