from src.chat.option import select_chat_mode
from src.chat.chat_auto import chat_auto
from src.preset import PAPER_PATH
from src.file_format import load_jsonl


DATASET_PATH = PAPER_PATH / 'dataset'


def test_fine_tune():

    chat_context = select_chat_mode()

    chat_context['papers'] = get_test_papers(chat_context)

    chat_func = chat_context['chat_func']
    del chat_context['chat_func']

    chat_auto(chat_context, chat_func)


def get_test_papers(chat_context):

    test_set_file = DATASET_PATH / 'by_paper' / 'test_set.jsonl'
    table = load_jsonl(test_set_file)
    pmids = list(set([
        str(i['PMID'])
        for i in table
    ]))

    print(len(pmids))

    paper_set = chat_context['test_set']

    papers = []
    for f in paper_set.iterdir():
        if not f.is_dir():
            continue
        if str(f.name) not in pmids:
            continue
        for i in f.iterdir():
            if 'checked.md' in i.name.lower():
                papers.append((i, i.name))

    print('# Papers', len(papers))

    return [
        p[0]
        for p in papers
    ]
