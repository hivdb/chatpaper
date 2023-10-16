from src.file_format import load_csv
from src.file_format import dump_csv
from src.table import group_records_by


def check_NA_correct_rate(save_path, data_files):

    report = []

    for i in data_files:
        report.extend(check_NA(i))

    dump_csv(save_path, report)


def check_NA(f):
    table = load_csv(f)

    groups = seperate_human_NA(table)

    num_agree = len([
        i
        for i in groups['Yes']
        if i['agree?'].lower().startswith('yes')
    ])

    report = []

    report.append({
        'mode': f.stem,
        'human_NA': 'Yes',
        'num_agree': num_agree,
        'num_total': len(groups['Yes']),
        '% agree': num_agree / len(groups['Yes'])
    })

    num_agree = len([
        i
        for i in groups['No']
        if i['agree?'].lower().startswith('yes')
    ])

    report.append({
        'mode': f.stem,
        'human_NA': 'No',
        'num_agree': num_agree,
        'num_total': len(groups['No']),
        '% agree': num_agree / len(groups['No'])
    })

    return report


def seperate_human_NA(table):

    return group_records_by(table, 'human_NA')

# def check_NA(f):
#     table = load_csv(f)

#     report = []

#     for key, q_list in group_records_by(table, ['question_id', 'human_NA']).items():

#         key = dict(key)

#         num_agree = len([
#             i
#             for i in q_list
#             if i['agree?'].lower() == 'yes'
#         ])

#         report.append({
#             'mode': f.stem,
#             'question_id': key['question_id'],
#             'human_NA': key['human_NA'],
#             'num_agree': num_agree,
#             'num_total': len(q_list),
#             '% agree': num_agree / len(q_list),
#         })

#     return report
