from src.select_content.test_set import select_test_set
from src.prepare_eval_file.update_human_answer import choose_checked_answer
from src.apis.chat_api import chat_ai
from src.select_content.prompt_template import load_prompt_template
from src.file_format import load_csv
from src.file_format import dump_csv


def auto_eval_answer(model='gpt-3.5-turbo-16k'):

    test_set_path = select_test_set()

    file_path = choose_checked_answer(test_set_path)

    prompt_template = load_prompt_template('auto_eval')

    records = load_csv(file_path)

    for i in records:
        q = i['question']
        a1 = i['human answer']
        a2 = i['AI answer']
        prompt = prompt_template.format(Q=q, A1=a1, A2=a2)

        resp = chat_ai(prompt, model)

        i['agree?'] = resp['answer']

    dump_csv(file_path, records)
