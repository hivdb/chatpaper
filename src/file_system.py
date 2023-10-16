from pathlib import Path


# TODO: replace template
def rename_batch(folder, pattern, replace):
    if type(folder) == str:
        folder = Path(folder)

    files = find_all_files(folder, pattern)

    for f in files:
        new_file_path = f.parent / f.name.replace(pattern, replace)
        f.rename(new_file_path)


def find_all_files(folder, pattern):

    files = []
    for i in folder.iterdir():

        if pattern in i.name:
            files.append(i)

        if i.is_dir():
            files.extend(find_all_files(i, pattern))

    return files
