import re
from bs4 import BeautifulSoup
from lxml.html import fragments_fromstring
from lxml.html import etree
import lxml
from src.logs import logger


def prepare_tables(file_context, file_key):
    src = file_context[file_key]

    new_file_key = file_key.replace('.clean.html', '.tables.md')

    dest = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    if dest.exists() and not file_context['_overwrite']:
        return

    all_table_names = find_table_names(src)

    table_html = {
        i: v
        for i, v in file_context.items()
        if i.lower().startswith('table')
    }

    tables = {}
    if table_html:
        tables = find_table_by_table_file(table_html)

    for name in all_table_names:
        if name not in tables:
            tables.update(find_tables(src, all_table_names))

    with open(dest, 'w') as fd:
        for i, v in tables.items():
            fd.write(f"## {i}\n\n{v}\n\n")

        for idx, i in enumerate(get_any_table(src)):
            fd.write(f"## Any table {idx}\n\n{i}\n\n")

    file_context['metadata']['tables'] = all_table_names


def find_table_names(html_file):
    with open(html_file) as fd:
        content = fd.read()

    matches = re.findall(
        r'(Table\s*\d+)', content, re.IGNORECASE)

    if not matches:
        logger.info('No Tables')

    all_table_names = sorted(set([
        re.sub(r'\s+', ' ', m.capitalize())
        for m in matches
    ]))

    return all_table_names


def find_table_by_table_file(table_html):

    found_tables = {}

    for table_name, html in table_html.items():
        match = re.match(
            r'table\s*(?P<id>\d+)', table_name, re.IGNORECASE).groupdict()
        table_name = f'Table {match["id"]}'

        with open(html) as fd:
            content = fd.read()

        elements = fragments_fromstring(content)

        for i in list(elements):
            if i.tag == 'table':
                tables = [i]
            else:
                tables = i.xpath('.//table')
            if not tables:
                continue

            for i in tables:
                table_str = etree.tostring(i, pretty_print=True).decode()

                table_data = keep_table_tags_only(table_str)

                found_tables[table_name] = table_data

    return found_tables


def find_tables(html_file, all_table_names):
    with open(html_file) as fd:
        content = fd.read()

    try:
        elements = fragments_fromstring(content)
    except lxml.etree.ParserError:
        return {}

    tables = {}

    for table_name in all_table_names:
        ele_list = find_table_element(elements, table_name)
        if not ele_list:
            tables[table_name] = f'**{table_name} not found**'
        else:
            tables[table_name] = '\n\n'.join(ele_list)

    return tables


def get_any_table(html_file):
    with open(html_file) as fd:
        content = fd.read()

    try:
        element = fragments_fromstring(content)
    except lxml.etree.ParserError:
        return []

    results = []

    for i in list(element):
        if i.tag == 'table':
            tables = [i]
        else:
            tables = i.xpath('.//table')

        if not tables:
            continue

        for i in tables:
            table_str = etree.tostring(i, pretty_print=True).decode()

            table_data = keep_table_tags_only(table_str)

            results.append(table_data)

    return results


def find_table_element(element, table_name):

    results = []
    for i in list(element):
        tags = i.xpath(f".//*[contains(text(), '{table_name.lower()}')]")
        tags += i.xpath(f".//*[contains(text(), '{table_name.capitalize()}')]")
        tags += i.xpath(f".//*[contains(text(), '{table_name.upper()}')]")
        for j in tags:
            table_tag = find_table_tag(j)
            if table_tag is None:
                continue

            table_html = etree.tostring(table_tag, pretty_print=True).decode()
            table_data = keep_table_tags_only(table_html)

            results.append(table_data)

    return results


def keep_table_tags_only(
        table_str,
        tags_to_keep=['table', 'thead', 'tr', 'th', 'td', 'sub', 'sup'],
        pretty=False):

    soup = BeautifulSoup(table_str, 'html.parser')

    for tag in soup.findAll(True):
        if tag.name not in tags_to_keep:
            tag.replaceWithChildren()
            continue

        for attr in dict(tag.attrs):
            if attr not in ['rowspan', 'colspan']:
                del tag.attrs[attr]

    if pretty:
        return soup.prettify()
    else:
        content = soup.prettify(formatter="minimal").replace('\n', '')
        content = re.sub(r">\s+<", "><", content)
        return content


def find_table_tag(element):
    if element is None:
        return None

    if element.tag == 'table':
        return element

    parent = element.getparent()
    return find_table_tag(parent)
