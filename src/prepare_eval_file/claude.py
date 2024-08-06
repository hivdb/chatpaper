from src.file_format import dump_csv
from src.excel2csv import load_excel
from operator import itemgetter

from .translate_answer.translate_AI_NA import translate_AI_NA
from .translate_answer.translate_AI_reply import translate_AI_reply
from .translate_answer.get_question_type import get_question_type
from .translate_answer.get_AI_reply import get_AI_reply
from .translate_answer.get_human_answer import get_human_answer
from .translate_answer.translate_human_NA import translate_human_NA

from src.evaluation.quick_eval import quick_eval
from src.evaluation.quick_eval import load_eval_db


def gen_claude_eval_file(test_set):

    papers = test_set / 'Papers'

    files = {}
    all_papers = set()

    for i in papers.iterdir():
        if not i.is_dir():
            continue

        all_papers.add(i.stem)

        for j in i.iterdir():
            if j.name.endswith('claude.xlsx'):
                files[i.stem] = j
            # if j.name.endswith('claude.csv'):
            #     files[i.stem] = j
            #     break

    verify_claude_files(files, all_papers)

    eval_db = load_eval_db(test_set / 'evaluation' / 'eval_db.csv')

    prepare_table(
        test_set / 'evaluation', files, 'claude_base', 'WO', eval_db)
    prepare_table(
        test_set / 'evaluation', files, 'claude_guide', 'WITH', eval_db)


def verify_claude_files(files, all_papers):
    for i in all_papers:
        if i not in files.keys():
            print(i)

    main_keys = [
        'Paper', 'question_id',
        'question', 'human answer',
        'WO version',
        'WO answer', 'WO agree?', 'WO explain',
        'WITH version',
        'WITH answer', 'WITH agree?', 'WITH explain'
        ]

    for f, j in files.items():
        content = load_excel(j)

        keys = content[0].keys()
        for i in keys:
            if not i:
                continue
            if i not in main_keys:
                print('Additional key', f, i)

        for i in main_keys:
            if i not in keys and not i.lower().endswith('version'):
                print('Missing key', f, i)

        for i in content:
            if i['Paper'] != f:
                print('Error paper', f, i['Paper'])


def prepare_table(save_path, files, mode, include_prefix, eval_db):

    table = []

    if include_prefix == 'WO':
        exclude_prefix = 'WITH'
    else:
        exclude_prefix = 'WO'

    for paper, f in files.items():
        content = load_excel(f)

        sub_table = []

        for i in content:

            for j in list(i.keys()):
                if not j:
                    del i[j]
                else:
                    i[j] = str(i[j])

            i.update({
                'chat_mode': mode,
                'model': 'claude',
                'paper': paper,
            })

            include_header = [
                k
                for k in i.keys()
                if k.startswith(include_prefix)
            ]

            exclude_header = [
                k
                for k in i.keys()
                if k.startswith(exclude_prefix)
            ]

            for k in exclude_header:
                del i[k]

            for k in include_header:
                i[k.replace(include_prefix, '').strip()] = i[k]

            del i['human answer']
            i['human_eval'] = i['agree?']
            del i['agree?']

            if 'version' in i:
                del i['version']

            sub_table.append(i)

        sub_table = get_question_type(sub_table)
        sub_table = get_AI_reply(sub_table)
        sub_table = translate_AI_NA(sub_table)
        sub_table = translate_AI_reply(sub_table)

        human_answer_file = f.parent / 'human_answer.csv'
        sub_table = get_human_answer(sub_table, human_answer_file)

        sub_table = translate_human_NA(sub_table)

        [quick_eval(i, eval_db) for i in sub_table]

        table.extend(sub_table)

    table.sort(key=itemgetter(
        'model', 'chat_mode',
        'paper', 'question_id'))

    dump_csv(
        save_path / f'{mode}.csv',
        table,
        headers=[
            'paper',
            'question_id',
            'question',
            'question_type',
            'human_answer',
            'human_NA',
            'AI_reply',
            'AI_NA',
            'AI_answer',
            'agree?',
            'human_eval',
            # 'rationale',
            'correct_rationale?',
            'evidence',
            'correct_evidence?',
            'model',
            'chat_mode',
        ],
        remain=False
        )
