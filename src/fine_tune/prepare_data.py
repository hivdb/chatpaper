from src.file_format import dump_jsonl
from src.file_format import load_csv
from src.excel2csv import load_excel
from src.preset import PAPER_PATH
from src.preset import PROMPT_TEMPLATE_PATH
from src.preset import QUESTION_PATH
import random


DATA_FILE = PAPER_PATH / 'Fine-tuning instruction set, Aug 3.xlsx'
SYSTEM_PROMPT = open(PROMPT_TEMPLATE_PATH / 'system.txt').read()
MAIN_PROMPT = open(PROMPT_TEMPLATE_PATH / 'explain_one_question.txt').read()
QUESTIONS = QUESTION_PATH / 'HIV_Set1_Jul8.csv'
ASSISTANT_PROMPT = open(PROMPT_TEMPLATE_PATH / 'assistant.txt').read()

DATASET_PATH = PAPER_PATH / 'dataset'
DATASET_PATH.mkdir(exist_ok=True)

VAL_SET_PMID = [
    20124001,
    20300008,
    20308382,
    20438383,
    20455758,
    20507208,
    20530226,
    20660667,
    20666602,
    20718620,
    21114823,
    21189351,
    21358627,
    21765953,
    25261422,
    25273080,
    25281399,
    25642847,
    25681380,
    25694653,
    26041893,
    26082240,
    29765018,
    33055182,
    34422316,
]

TEST_SET_PMID = [
    19686436,
    19913270,
    19917747,
    19933171,
    19933797,
    19938977,
    20008779,
    20029816,
    20345882,
    20388636,
    20398371,
    20426823,
    20430786,
    20453629,
    20643915,
    20702636,
    34422316,
    35305571,
    36082606,
    36101479,
    36347497,
    36708743,
    37293603,
    38141637,
    38376918
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

    print('# Papers', len(paper_content))

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

    for i in table:
        pmid = str(i['PMID'])
        i['paper_content'] = paper_content[pmid]

    for i in table:
        i['system'] = SYSTEM_PROMPT

    for i in table:
        qid = str(i['QID'])
        ques = questions[qid]
        prompt = MAIN_PROMPT.format(
            question=ques['question'],
            question_prompt=ques['prompt'],
            paper_content=i['paper_content'])

        i['question prompt'] = ques['prompt']
        i['user'] = prompt

    for i in table:
        i['assistant'] = ASSISTANT_PROMPT.format(
            answer=i['Answer'],
            rationale=i['Rationale'],
            sentences=i['Reference Sentences']
        )
        i['Answer'] = str(i['Answer'])

    dump_jsonl(DATASET_PATH / 'pre_dataset.jsonl', table)

    # for i in table:
    #     if str(i['PMID']) == '20004217' and str(i['QID']) == '17':
    #         print(i['system'])
    #         print(i['user'])
    #         print(i['assistant'])

    dataset = [
        {
            'messages': [
                {"role": "system", "content": i['system']},
                {"role": "user", "content": i['user']},
                {"role": "assistant", "content": i['assistant']},
            ]
        }
        for i in table
    ]
    dump_jsonl(DATASET_PATH / 'dataset.jsonl', dataset)

    save_path = DATASET_PATH / 'by_paper'
    save_path.mkdir(exist_ok=True)
    split_by_paper(save_path, table)

    save_path = DATASET_PATH / 'by_question'
    save_path.mkdir(exist_ok=True)
    split_by_question(save_path, table)


def split_by_question(save_path, table):
    random.shuffle(table)

    # Calculate the size of each set
    test_size = int(0.15 * len(table))
    validation_size = int(0.15 * len(table))
    # training_size = len(pmid_list) - test_size - validation_size

    test_set = table[:test_size]
    val_set = table[test_size:test_size + validation_size]
    train_set = table[test_size + validation_size:]

    dump_dataset_jsonl(save_path, train_set, val_set, test_set)


def split_by_paper(save_path, table):
    pmid_list = list(set([
        i['PMID']
        for i in table
    ]))

    _, VAL_SET_PMID, TEST_SET_PMID = random_dataset_by_pmid(pmid_list)

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
        for i in table
        if (int(i['PMID']) in TEST_SET_PMID)
    ]

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

    train_set = [
        {
            'messages': [
                {"role": "system", "content": i['system']},
                {"role": "user", "content": i['user']},
                {"role": "assistant", "content": i['assistant']},
            ]
        }
        for i in train_set
    ]

    dump_jsonl(save_path / 'train_set.jsonl', train_set)

    val_set = [
        {
            'messages': [
                {"role": "system", "content": i['system']},
                {"role": "user", "content": i['user']},
                {"role": "assistant", "content": i['assistant']},
            ]
        }
        for i in val_set
    ]

    dump_jsonl(save_path / 'val_set.jsonl', val_set)

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
