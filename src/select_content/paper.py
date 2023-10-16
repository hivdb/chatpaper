from prompt_toolkit.shortcuts import radiolist_dialog
from prompt_toolkit.shortcuts import checkboxlist_dialog
from src.exceptions import check_selection
from src.preset import DEFAULT_OPTIONS


def select_paper_content(test_set_folder, all_option=False, only_one=False):
    test_set_folder = test_set_folder / 'Papers'

    file_format = select_paper_file_format()

    papers = select_some_paper_content(
        test_set_folder,
        file_format=file_format,
        all_option=all_option,
        only_one=only_one)

    papers = papers if type(papers) is list else [papers]

    if 'all' in papers:
        return [
            i[0] for i in list_paper_content(file_format, test_set_folder)]
    else:
        return papers


PAPER_FORMATS = {
    'checked.md':
        'Checked method and result file with figures and tables',
    # 'method_and_result.html.md':
    #     'Methods and results markdown file with figures and tables',
    # 'clean.html.md':
    #     'html2markdown file',
    # '.docx.md':
    #     'docx2markdown file',
    # '.pdf.md':
    #     'pdf2makdown file',
    # '.pdf.txt':
    #     'pdf2txt file',
}


def list_paper_file_format():
    return [
        (k, v)
        for k, v in PAPER_FORMATS.items()
    ]


@check_selection()
def select_paper_file_format(
        title='Please select the format of text you want to feed to AI',
        desc='',
        default=list_paper_file_format()[0][0]
        ):

    if 'file_format' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('file_format')

    result = radiolist_dialog(
        title=title,
        text=desc,
        values=list_paper_file_format(),
        default=default
    ).run()

    return result


def list_paper_content(file_format, folder):
    papers = []
    for f in folder.iterdir():
        if not f.is_dir():
            continue

        document_path = f / 'document'

        if not document_path.exists():
            continue

        for i in document_path.iterdir():
            if file_format in i.name.lower():
                papers.append((i, i.name))

    papers.sort(key=lambda x: x[-1])
    return papers


@check_selection()
def select_some_paper_content(
        paper_folder,
        title="Please choose paper.",
        file_format='',
        all_option=False, only_one=False):

    if 'papers' in DEFAULT_OPTIONS:
        return DEFAULT_OPTIONS.get('papers')

    papers = list_paper_content(file_format, paper_folder)

    num_paper = len(papers)
    if only_one:
        dialog = radiolist_dialog
    else:
        dialog = checkboxlist_dialog

    if all_option and not only_one:
        papers.insert(0, ('all', 'All'))

    result = dialog(
        title=title,
        text=f'{num_paper} papers in this Set',
        values=papers
    ).run()

    return result


def select_paper(test_set_folder, all_option=True, only_one=False):
    test_set_folder = test_set_folder / 'Papers'

    # TODO, show number of papers

    folders = select_some_paper(
        test_set_folder,
        all_option=all_option,
        only_one=only_one)

    folders = folders if type(folders) is list else [folders]

    if 'all' in folders:
        return [
            i[0] for i in list_paper(test_set_folder)]
    else:
        return folders


def list_paper(folder):
    paper_path_list = []
    for i in folder.iterdir():
        if not i.is_dir():
            continue
        paper_path_list.append((i, i.name))

    paper_path_list.sort(key=lambda x: x[-1])

    return paper_path_list


@check_selection()
def select_some_paper(
        folder, title="Please select paper.", desc='',
        all_option=False, only_one=False):

    if only_one:
        dialog = radiolist_dialog
    else:
        dialog = checkboxlist_dialog

    folders = list_paper(folder)
    if all_option and not only_one:
        folders.insert(0, ('all', 'All'))

    result = dialog(
        title=title,
        text=desc,
        values=folders,
    ).run()

    return result
