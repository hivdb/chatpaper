from src.doc_format.process_html import prepare_clean_html
from src.doc_format.process_html import prepare_docx_html
from src.doc_format.process_html import prepare_html_md
from .method_and_result import prepare_method_and_result
from .table import prepare_tables
from .figure import prepare_figures
from .combine import combine_content
from src.file_format import dump_json
from src.apis.embedding import get_token_length
from src.apis.embedding import get_vectordb
from src.file_format import dump_csv
from src.file_format import load_csv
from src.file_format import load_json
from src.logs import logger
from src.select_content.test_set import select_test_set
from src.select_content.paper import select_paper
from src.preset import PAPER_PATH
from .option import choose_overwrite
from .option import choose_generate_embedding


def batch_prepare_files():

    test_set_path = select_test_set()
    overwrite_option = choose_overwrite()
    embedding_option = choose_generate_embedding()

    file_context_list = prepare_file_context_list(test_set_path, {
        '_overwrite': overwrite_option,
        '_embedding': embedding_option
    })

    for file_context in file_context_list:
        logger.info(f"Processing... {file_context['main_name']}")
        logger.debug(file_context)

        if '.html' in file_context:
            file_context['sub_folder'] = 'html'
            (file_context['doc_folder'] / file_context['sub_folder']).mkdir(
                exist_ok=True)

            prepare_clean_html(file_context, '.html')
            prepare_html_md(file_context, '.clean.html')
            prepare_method_and_result(file_context, '.clean.md')
            prepare_figures(file_context, '.clean.html')
            prepare_tables(file_context, '.clean.html')

        if '.docx' in file_context:
            file_context['sub_folder'] = 'docx'
            (file_context['doc_folder'] / file_context['sub_folder']).mkdir(
                exist_ok=True)

            prepare_docx_html(file_context)
            prepare_clean_html(file_context, '.docx.html')
            prepare_html_md(file_context, '.docx.clean.html')
            prepare_method_and_result(file_context, '.docx.clean.md')
            prepare_figures(file_context, '.docx.clean.html')
            prepare_tables(file_context, '.docx.clean.html')

        combine_content(file_context)
        dump_metadata(file_context)

        for i in file_context['doc_folder'].iterdir():
            if '.checked.md' in i.name:
                file_context['.checked.md'] = i

        if file_context['_embedding']:
            embedding_paper(file_context, '.checked.md')

    collect_paper_summary(test_set_path, file_context_list)

    collect_all_paper_summary(folder=PAPER_PATH)


def prepare_file_context_list(folder, parameters={}):

    paper_folders = select_paper(folder)

    context_list = []
    for d in paper_folders:

        file_context = {
            'main_name': d.stem,
            'metadata': {}
        }
        file_context.update(parameters)

        for f in d.iterdir():
            if f.suffix.lower() == '.html':
                if 'table' in f.name.lower():
                    file_context[f.stem] = f
                else:
                    file_context['.html'] = f
            if f.suffix.lower() == '.docx':
                file_context['.docx'] = f

        if not file_context.get('.html') and not file_context.get('.docx'):
            continue

        doc_folder = d / 'document'

        if parameters.get('clean'):
            remove_temp_folder(doc_folder)
            continue

        doc_folder.mkdir(parents=True, exist_ok=True)

        file_context['doc_folder'] = doc_folder
        context_list.append(file_context)

    return context_list


def embedding_paper(file_context, file_format):
    if '.checked.md' not in file_context:
        return
    file_path = file_context[file_format]
    get_vectordb(file_path, file_context['doc_folder'], 'paragraph')
    get_vectordb(file_path, file_context['doc_folder'], 'section')


def remove_temp_folder(doc_folder):
    # if doc_folder.exists():
    #     shutil.rmtree(doc_folder)

    if not doc_folder.exists():
        return

    for i in doc_folder.iterdir():
        if 'checked' not in i.name:
            i.unlink()


def dump_metadata(file_context):
    save_path = (
        file_context['doc_folder'] /
        f"{file_context['main_name']}.meta.json"
    )

    cheched = (
        file_context['doc_folder'] /
        f"{file_context['main_name']}.checked.md"
    )
    if cheched.exists():
        with open(cheched) as fd:
            file_context['metadata']['token_length'] = get_token_length(
                fd.read())

    dump_json(save_path, file_context['metadata'])


def collect_paper_summary(test_set_path, file_context_list):

    report = []

    for file_context in file_context_list:
        metadata_file = (
            file_context['doc_folder'] /
            f"{file_context['main_name']}.meta.json")

        metadata = load_json(metadata_file)

        report.append({
            'name': file_context['main_name'],
            'token_length': metadata.get('token_length'),
            'tables': ', '.join(metadata.get('tables', [])),
            'figures': ', '.join(metadata.get('figures', [])),
        })

    dump_csv(test_set_path / 'papers_infomation.csv', report)


def collect_all_paper_summary(folder=PAPER_PATH):

    result = []

    for i in folder.iterdir():
        if not i.is_dir():
            continue

        if not i.name.startswith('Set'):
            continue

        info_file = i / 'papers_infomation.csv'
        result.extend(load_csv(info_file))

    dump_csv(folder / 'papers_information.csv', result)
