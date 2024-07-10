from bs4 import BeautifulSoup
from bs4 import Comment
from .converter import html2md_pandoc
from .converter import docx2html_pandoc


def prepare_clean_html(file_context, file_key):
    src = file_context[file_key]

    new_file_key = file_key.replace('.html', '.clean.html')
    dest = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    with open(src) as fd:
        html_content = clean_html(fd.read())

    with open(dest, 'w') as fd:
        fd.write(html_content)


def clean_html(html):
    soup = BeautifulSoup(html, 'html.parser')

    for element in soup.findAll("span", {"class" : "tag-json"}):
        element.decompose()

    for script in soup(["script", "style"]):
        script.decompose()

    for tag in soup():
        attrs_to_delete = [attr for attr in tag.attrs if attr not in ('colspan', 'rowspan')]
        for attr in attrs_to_delete:
            del tag[attr]

    for comment in soup.find_all(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    return soup.prettify()


def prepare_html_md(file_context, file_key):
    src = file_context[file_key]

    new_file_key = file_key.replace('.html', '.md')
    dest = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    if dest.exists() and not file_context['_overwrite']:
        return

    html2md_pandoc(src, dest)


def prepare_docx_html(file_context):

    docx_html = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f'{file_context["main_name"]}.docx.html')
    file_context['.docx.html'] = docx_html

    docx2html_pandoc(file_context['.docx'], docx_html)
