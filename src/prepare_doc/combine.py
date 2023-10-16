def combine_content(file_context):

    if '.method_and_result.md' not in file_context:
        return

    method_file_path = file_context['.method_and_result.md']
    content = ''

    if method_file_path.exists():
        with open(method_file_path) as fd:
            content += fd.read()
            content += '\n\n'

    figure_file_path = file_context['.figures.md']

    if figure_file_path.exists():
        with open(figure_file_path) as fd:
            content += fd.read()
            content += '\n\n'

    table_file_path = file_context['.tables.md']

    if table_file_path.exists():
        with open(table_file_path) as fd:
            content += fd.read()
            content += '\n\n'

    new_file_key = '.combined.md'
    dest = (
        file_context['doc_folder'] /
        f"{file_context['main_name']}{new_file_key}"
    )
    file_context[new_file_key] = dest

    with open(dest, 'w') as fd:
        fd.write(content)
