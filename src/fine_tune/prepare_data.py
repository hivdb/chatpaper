from src.file_format import dump_jsonl
from src.file_format import load_csv, dump_csv
from src.excel2csv import load_excel
from src.preset import PAPER_PATH
from src.preset import PROMPT_TEMPLATE_PATH
from src.preset import QUESTION_PATH
import random
from src.table import group_records_by
import tiktoken
from operator import itemgetter
from collections import defaultdict


DATA_FILE = PAPER_PATH / 'Fine-tuning instruction set, Aug 22.xlsx'
SYSTEM_PROMPT = open(PROMPT_TEMPLATE_PATH / 'system.txt').read()
MAIN_PROMPT = open(PROMPT_TEMPLATE_PATH / 'explain_multi_questions.txt').read()
QUESTIONS = QUESTION_PATH / 'HIV_Set1_Aug19.csv'
ASSISTANT_PROMPT = open(PROMPT_TEMPLATE_PATH / 'assistant.txt').read()
QUESTION_PROMPT = open(PROMPT_TEMPLATE_PATH / 'question_prompt.txt').read()
PAPER_SPLIT = PAPER_PATH / 'Fine-tuning instruction set, Aug 22_split.csv'
TEST_FILE = PAPER_PATH / 'Testset_Aug23.xlsx'
TEST_FILE = PAPER_PATH / 'Testset_20251202.xlsx'

DATASET_PATH = PAPER_PATH / 'dataset'
DATASET_PATH.mkdir(exist_ok=True)

VAL_SET_PMID = [
    int(i['PMID'])
    for i in load_csv(PAPER_SPLIT)
    if i['category'] == 'val'
    ]

TEST_SET_PMID = [
    int(i['PMID'])
    for i in load_excel(TEST_FILE)
    ]


def load_paper_markdown(papers=PAPER_PATH):

    both_eval_test = set(VAL_SET_PMID) & set(TEST_SET_PMID)

    print('#Val, test set overlap:', both_eval_test)
    print('#val set:', len(set(VAL_SET_PMID)))
    print('#test set:', len(set(TEST_SET_PMID)))

    paper_content = {}

    for i in papers.iterdir():
        if not i.is_dir():
            continue
        if not i.name.startswith('paper'):
            continue

        for pmid in i.iterdir():
            if not pmid.is_dir():
                continue

            for f in pmid.iterdir():
                if not f.name.endswith('checked.md'):
                    continue

                paper_content[pmid.name] = open(f).read()

    print('# Processed Papers', len(paper_content))

    return paper_content


def load_question(quetions=QUESTIONS):
    result = {}
    for i in load_csv(quetions):
        result[i['id']] = i

    return result


def prepare_data():
    paper_content = load_paper_markdown()
    questions = load_question()

    table = load_excel(DATA_FILE)

    # table = [
    #     i
    #     for i in table
    #     if str(i['Done']).strip() == '1'
    # ]

    print('#Sample for fine tuning', len(table))

    # table = add_prompt_info(table, paper_content, questions)

    # dump_jsonl(DATASET_PATH / 'single_question.jsonl', table)
    # show_one_example(table, DATASET_PATH / 'single_question.txt')

    test_table = load_excel(TEST_FILE)
    test_table = add_prompt_info(test_table, paper_content, questions)

    # save_path = DATASET_PATH / 'by_question'
    # save_path.mkdir(exist_ok=True)
    # split_by_question(save_path, table, test_table)

    # # multi question

    # table = format_multi_ques_dataset(table)

    # show_one_example(table, DATASET_PATH / 'multi_question.txt')

    # # for i in table:
    # #     if str(i['PMID']) == '20004217' and str(i['QID']) == '17':
    # #         print(i['system'])
    # #         print(i['user'])
    # #         print(i['assistant'])

    # dataset = [
    #     {
    #         'messages': [
    #             {"role": "system", "content": i['system']},
    #             {"role": "user", "content": i['user']},
    #             {"role": "assistant", "content": i['assistant']},
    #         ],
    #         # 'PMID': i['PMID']
    #     }
    #     for i in table
    # ]
    # dump_jsonl(DATASET_PATH / 'multiple_question.jsonl', dataset)

    save_path = DATASET_PATH / 'by_paper'
    save_path.mkdir(exist_ok=True)
    test_table = format_multi_ques_dataset(test_table)
    split_by_paper(save_path, table, test_table)


def add_prompt_info(table, paper_content, questions):
    for i in table:
        pmid = str(i['PMID'])
        i['paper_content'] = paper_content[pmid]

    for i in table:
        i['system'] = SYSTEM_PROMPT

    table = [
        i
        for i in table
        if str(i['QID']) in questions.keys()
    ]

    for i in table:
        qid = str(i['QID'])
        ques = questions[qid]
        prompt = QUESTION_PROMPT.format(
            question_id=ques['id'],
            question=ques['question'],
            instruction=ques['instruction'])

        i['instruction'] = ques['instruction']
        i['question_prompt'] = prompt
        i['Answer'] = str(i['Answer'])

    # single question

    for i in table:
        i['user'] = MAIN_PROMPT.format(
            paper_content=i['paper_content'],
            question=i['question_prompt']
        )

    for i in table:
        i['assistant'] = ASSISTANT_PROMPT.format(
            question=i['Question'],
            answer=i['Answer'],
            rationale=i.get('Rationale', ''),
            evidence=i.get('Evidence', ''),
        )

    table = calc_prompt_token(table)

    return table


def format_multi_ques_dataset(table):
    new_table = []

    for pmid, pmid_list in group_records_by(table, 'PMID').items():
        item = pmid_list[0]
        item['question_prompt'] = '\n'.join([
            i['question_prompt']
            for i in pmid_list
        ])
        item['user'] = MAIN_PROMPT.format(
            paper_content=item['paper_content'],
            question=item['question_prompt']
        )
        item['assistant'] = '\n'.join([
            i['assistant']
            for i in pmid_list
        ])
        new_table.append(item)

    new_table = calc_prompt_token(new_table)

    return new_table


def calc_prompt_token(table):

    encoding = tiktoken.encoding_for_model('gpt-4o')

    for item in table:
        item['#system_token'] = len(encoding.encode(item['system']))
        item['#user_token'] = len(encoding.encode(item['user']))
        item['#input_token'] = item['#system_token'] + item['#user_token']
        item['#assistant'] = len(encoding.encode(item['assistant']))
        item['#total_token'] = item['#input_token'] + item['#assistant']

    table.sort(key=lambda x: (-x['#total_token'], -x['#input_token']))
    return table


def split_by_question(save_path, table, test_table):
    train_set = [
        i
        for i in table
        if (
                (int(i['PMID']) not in VAL_SET_PMID)
                and
                (int(i['PMID']) not in TEST_SET_PMID)
        )
    ]

    prob_question_number(train_set)
    val_set = [
        i
        for i in table
        if (int(i['PMID']) in VAL_SET_PMID)
    ]

    prob_question_number(val_set)

    test_set = [
        i
        for i in test_table
        if (int(i['PMID']) in TEST_SET_PMID)
    ]

    prob_question_number(test_set)

    dump_csv(save_path / 'train_token.csv', train_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    dump_csv(save_path / 'val_token.csv', val_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    dump_csv(save_path / 'test_token.csv', test_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    # train_set = [
    #     i
    #     for i in train_set
    #     if i['#total_token'] < 10000
    # ]

    # val_set = [
    #     i
    #     for i in val_set
    #     if i['#total_token'] < 10000
    # ]

    dump_dataset_jsonl(save_path, train_set, val_set, test_set)


def prob_question_number(table):
    question_count = defaultdict(int)

    for i in table:
        question_count[i['QID']] += 1

    for i, j in question_count.items():
        print('Q:', i, j)


def split_by_paper(save_path, table, test_table):
    # pmid_list = list(set([
    #     i['PMID']
    #     for i in table
    # ]))
    # _, VAL_SET_PMID, TEST_SET_PMID = random_dataset_by_pmid(pmid_list)

    train_set = [
        i
        for i in table
        if (
                (int(i['PMID']) not in VAL_SET_PMID)
                and
                (int(i['PMID']) not in TEST_SET_PMID)
        )
    ]
    val_set = [
        i
        for i in table
        if (int(i['PMID']) in VAL_SET_PMID)
    ]

    test_set = [
        i
        for i in test_table
        if (int(i['PMID']) in TEST_SET_PMID)
    ]

    dump_csv(save_path / 'train_token.csv', train_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    dump_csv(save_path / 'val_token.csv', val_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    dump_csv(save_path / 'test_token.csv', test_set, headers=[
        'PMID', '#system_token', '#user_token', '#input_token',
        '#assistant', '#total_token'], remain=False)

    # train_set = [
    #     i
    #     for i in train_set
    #     if i['#total_token'] < 10000
    # ]

    # val_set = [
    #     i
    #     for i in val_set
    #     if i['#total_token'] < 10000
    # ]

    dump_dataset_jsonl(save_path, train_set, val_set, test_set)


def random_dataset_by_pmid(pmid_list):
    random.shuffle(pmid_list)

    # Calculate the size of each set
    test_size = int(0.15 * len(pmid_list))
    validation_size = int(0.15 * len(pmid_list))
    # training_size = len(pmid_list) - test_size - validation_size

    test_set = pmid_list[:test_size]
    validation_set = pmid_list[test_size:test_size + validation_size]
    training_set = pmid_list[test_size + validation_size:]

    return training_set, validation_set, test_set


def dump_dataset_jsonl(save_path, train_set, val_set, test_set):

    print('#Train', len(train_set))
    print('#Val', len(val_set))
    print('#Test', len(test_set))

    # train_set = [
    #     {
    #         'messages': [
    #             {"role": "system", "content": i['system']},
    #             {"role": "user", "content": i['user']},
    #             {"role": "assistant", "content": i['assistant']},
    #         ],
    #         # 'PMID': i['PMID']
    #     }
    #     for i in train_set
    # ]

    # dump_jsonl(save_path / 'train_set.jsonl', train_set)

    # val_set = [
    #     {
    #         'messages': [
    #             {"role": "system", "content": i['system']},
    #             {"role": "user", "content": i['user']},
    #             {"role": "assistant", "content": i['assistant']},
    #         ],
    #         # 'PMID': i['PMID']
    #     }
    #     for i in val_set
    # ]

    # dump_jsonl(save_path / 'val_set.jsonl', val_set)

    test_set = [
        {
            'messages': [
                {"role": "system", "content": i['system']},
                {"role": "user", "content": i['user']},
                {"role": "assistant", "content": i['assistant']},
            ]
        }
        for i in test_set
    ]

    dump_jsonl(save_path / 'test_set.jsonl', test_set)


def show_one_example(table, save_path):
    row = table[0]
    with open(save_path, 'w') as fd:
        fd.write(row['system'])
        fd.write('-' * 80)
        fd.write('\n\n')
        fd.write(row['user'])
        fd.write('-' * 80)
        fd.write('\n\n')
        fd.write(row['assistant'])
