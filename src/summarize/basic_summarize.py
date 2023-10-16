from src.file_format import load_csv
from src.file_format import dump_csv
from itertools import combinations


def summarize_agreement(table_path):

    table = load_csv(table_path)
    total = len(table)

    headers = list(table[0].keys())
    headers.remove('paper')
    headers.remove('question_id')
    headers.remove('question')
    headers.remove('question_type')
    headers.remove('# agree')

    num_agree = {}

    for k in headers:
        num_agree[k] = len([
                r
                for r in table
                if int(r[k])
            ])

    result = []

    for k, v in num_agree.items():
        result.append({
            'name': f'{k} agree',
            'value': f'{round(v * 100 / total, 1)}% ({v}/{total})'
        })

    num_getting_better = len([
        r
        for r in table
        if not int(r[headers[0]]) and int(r[headers[1]])
    ])
    result.append({
        'name': 'Getting better',
        'value': num_getting_better
    })
    num_getting_worse = len([
        r
        for r in table
        if int(r[headers[0]]) and not int(r[headers[1]])
    ])
    result.append({
        'name': 'Getting worse',
        'value': num_getting_worse
    })

    dump_csv(table_path.parent / 'summarize_agreement.csv', result)

    result = []

    for num_combi in range(1, len(headers) + 1):
        for combi in combinations(headers, num_combi):
            name = ' and '.join(combi)
            name = (
                f'{name} agree with Human'
                if num_combi > 1 else
                f'only {name} agree with Human')

            not_combi = [
                h
                for h in headers
                if h not in combi
            ]

            value = len([
                r
                for r in table
                if all(
                    int(r[s])
                    for s in combi
                ) and not any(
                    int(r[s])
                    for s in not_combi
                )
            ])
            rec = {
                'name': name,
                'all questions':  (
                    f'{round(value * 100 / total, 1)}% ({value}/{total})')
            }

            for k, v in num_agree.items():

                if k in rec['name']:

                    rec[f'any questions {k} agree with Human'] = (
                        f'{round(value * 100 / v, 1)}% ({value}/{v})'
                    )

            result.append(rec)

    not_agree = len([
        r
        for r in table
        if not any([
            int(r[h])
            for h in headers
        ])
    ])

    rec = {
        'name': 'not agree',
        'all questions': (
             f'{round(not_agree * 100 / total, 1)}% ({not_agree}/{total})'
        )
    }

    result.append(rec)

    dump_csv(table_path.parent / 'summarize_agree_detail.csv', result)
