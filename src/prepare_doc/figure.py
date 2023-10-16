import re
from lxml.html import fragments_fromstring
from lxml.html import etree
import lxml
from bs4 import BeautifulSoup
from src.logs import logger


def prepare_figures(file_context, file_key):
    src = file_context[file_key]

    new_file_key = file_key.replace('.clean.html', '.figures.md')

    dest = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    if dest.exists() and not file_context['_overwrite']:
        return

    all_figure_names = get_figure_names(src)
    # print('Figures:', all_figure_names, src)

    with open(dest, 'w') as fd:
        for i in find_figures(src, all_figure_names):
            fd.write(i)

    file_context['metadata']['figures'] = all_figure_names


def get_figure_names(html_file):
    with open(html_file) as fd:
        content = fd.read()

    content = content.replace('&nbsp;', ' ')
    matches = re.findall(
        r'((?:Figure|Fig)\.?\s*\d+)', content, re.IGNORECASE)

    if not matches:
        logger.info('No Figures')

    all_figure_names = sorted(set([
        re.sub(r'\s+', ' ', m.capitalize())
        for m in matches
    ]))

    return all_figure_names


def find_figures(html_file, all_figure_names):
    with open(html_file) as fd:
        content = fd.read()

    content = content.replace('&nbsp;', ' ')
    try:
        elements = fragments_fromstring(content)
    except lxml.etree.ParserError:
        return []

    figure_content = []

    for figure_name in all_figure_names:
        ele_list = find_figure_element(elements, figure_name)
        if not ele_list:
            figure_content.append(f'**{figure_name} not found**\n\n')
        else:
            figure_content.extend([
                f'{i}\n'
                for i in ele_list
            ])

    return figure_content


def find_figure_element(element, figure_name):
    results = []
    for i in list(element):
        tags = i.xpath(
            f".//*[contains(text(), '{figure_name.lower()}')]")
        tags += i.xpath(
            f".//*[contains(text(), '{figure_name.capitalize()}')]")
        tags += i.xpath(
            f".//*[contains(text(), '{figure_name.upper()}')]")

        for j in tags:
            figure_tag = find_figure_tag(j)
            if figure_tag is None:
                figure_tag = find_figure_tag(j, ['p'])
                if figure_tag is None:
                    figure_tag = find_figure_tag(j, ['div'])
                    if figure_tag is None:
                        continue

            figure_tag = remove_tags(figure_tag)
            figure_data = BeautifulSoup(figure_tag, 'html.parser').get_text()
            figure_data = re.sub(r'\s+', ' ', figure_data).strip()

            figure_data = figure_data[figure_data.lower().find('fig'):]

            if not re.match(
                    r'((?:Figure|Fig)\.?\s*\d+\.?(\s+[^)]|\:))',
                    figure_data, re.IGNORECASE):
                continue

            results.append(f"## {figure_name}\n\n{figure_data}\n\n")

    return results


def find_figure_tag(element, tag_list=['figure']):
    if element is None:
        return None

    if element.tag.lower() in tag_list:
        return element

    parent = element.getparent()
    return find_figure_tag(parent, tag_list)


def remove_tags(
        table, tags_to_remove=['button']):

    table = etree.tostring(table, pretty_print=True).decode()

    soup = BeautifulSoup(table, 'html.parser')

    for tag in soup.findAll(True):
        if tag.name in tags_to_remove:
            tag.extract()

    return soup.prettify()
