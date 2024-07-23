from src.file_format import dump_jsonl
from src.file_format import load_csv
from src.excel2csv import load_excel
from src.preset import PAPER_PATH
from src.preset import PROMPT_TEMPLATE_PATH
from src.preset import QUESTION_PATH


DATA_FILE = PAPER_PATH / 'Fine-tuning instruction set, Jul 22.xlsx'
SYSTEM_PROMPT = open(PROMPT_TEMPLATE_PATH / 'system.txt').read()
MAIN_PROMPT = open(PROMPT_TEMPLATE_PATH / 'explain_one_question.txt').read()
QUESTIONS = QUESTION_PATH / 'HIV_Set1_Jul8.csv'
ASSISTANT_PROMPT = open(PROMPT_TEMPLATE_PATH / 'assistant.txt').read()


def load_paper_markdown(papers=PAPER_PATH):

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

    table = [
        i
        for i in table
        if str(i['Done']).strip() == '1'
    ]

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

        i['user'] = prompt

    for i in table:
        i['assistant'] = ASSISTANT_PROMPT.format(
            answer=i['Answer'],
            rationale=i['Rationale'],
            sentences=i['Reference Sentences']
        )

    dump_jsonl(PAPER_PATH.parent / 'pre_dataset.jsonl', table)

    # for i in table:
    #     if str(i['PMID']) == '20004217' and str(i['QID']) == '17':
    #         print(i['system'])
    #         print(i['user'])
    #         print(i['assistant'])

    table = [
        {
            'messages': [
                {"role": "system", "content": i['system']},
                {"role": "user", "content": i['user']},
                {"role": "assistant", "content": i['assistant']},
            ]
        }
        for i in table
    ]

    dump_jsonl(PAPER_PATH.parent / 'dataset.jsonl', table)
