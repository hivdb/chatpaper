import re
from src.logs import logger


def prepare_method_and_result(file_context, file_key):
    src = file_context[file_key]

    new_file_key = file_key.replace('.clean.md', '.method_and_result.md')

    dest = (
        file_context['doc_folder'] / file_context['sub_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    if dest.exists() and not file_context['_overwrite']:
        return

    meta_data = extract_method_and_result(
        src, dest)

    file_context['metadata'].update(meta_data)


def split_md_section(full_md):

    # TODO: use markdown module
    sections = {}
    this_section = []
    this_section_name = 'head_content'
    for i in full_md.split('\n'):
        if i.startswith('# '):
            sections[this_section_name] = '\n'.join(this_section)
            this_section = [i]
            this_section_name = 'title'
            continue
        if i.startswith('## '):
            sections[this_section_name] = '\n'.join(this_section)
            this_section = [i]

            i = i[2:]
            match = re.search(r'[^A-Za-z\d\s\.]', i)
            if match:
                i = i[:match.start()].strip()
            this_section_name = i.lower()

            continue

        this_section.append(i)

    if this_section_name not in sections:
        sections[this_section_name] = '\n'.join(this_section)

    return sections


def extract_method_and_result(src, dest):
    # TODO: header in H3
    with open(src) as fd:
        full_md = fd.read()

    sections = split_md_section(full_md)

    result = []

    section_names = list(sections.keys())

    for i in ['abstract', 'method', 'result', 'discussion']:
        if any([i in j.lower() for j in section_names]):
            continue

        logger.info('Section names')
        logger.info(section_names)
        break

    meta_data = {}

    for k, v in sections.items():
        if 'reference' in k:
            continue
        result.append(v)

    # for k, v in sections.items():
    #     if 'title' in k:
    #         v = v.split('\n')[0]
    #         result.append(v)
    #         meta_data['title'] = True
    #     if 'method' in k:
    #         result.append(v)
    #         meta_data['method'] = True
    #     if 'result' in k:
    #         result.append(v)
    #         meta_data['result'] = True

    result = [
        remove_non_markdown(i)
        for i in result
    ]

    result = [
        reduce_new_line(i)
        for i in result
    ]

    result = '\n\n'.join(result)

    result = result.split('\n')

    result = [
        i
        for i in result
        if i.strip() != 'Go to:'
    ]

    result = '\n'.join(result)

    start_of_title = result.index('# ')
    if start_of_title > 0:
        result = result[start_of_title:]

    with open(dest, 'w') as fd:
        fd.write(result)

    return meta_data


def remove_non_markdown(text):
    # TODO, debug
    text = text.replace(
        '<div>\n', '').replace(
        '</div>\n', '').replace(
        '::: section\n', '').replace(
        ':::\n', '')

    new_text = []
    find_figure = False
    for i in text.split('\n'):
        if i.strip().lower() == '<figure>':
            find_figure = True
        elif find_figure and i.strip().lower() == '</figure>':
            find_figure = False
        elif not find_figure:
            new_text.append(i)

    text = '\n'.join(new_text)

    new_text = []
    for i in text.split('\n'):
        if i.startswith('![](') and i.endswith(')'):
            continue
        new_text.append(i)

    text = '\n'.join(new_text)

    return text


def reduce_new_line(text):
    new_text = []
    prev = ''
    for i in text.split('\n'):
        i = i.strip()
        if i:
            new_text.append(i)
            prev = i
            continue
        if prev == '':
            continue
        new_text.append(i)
        prev = i

    return '\n'.join(new_text)
