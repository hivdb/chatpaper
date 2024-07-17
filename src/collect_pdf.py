from src.preset import PAPER_PATH, WS
from shutil import copy

def collect_pdf(path=PAPER_PATH):

    pdfs = []
    for i in path.iterdir():
        if not i.is_dir():
            continue

        if not i.name.startswith('papers'):
            continue

        if 'candidate' in i.name:
            continue

        for j in i.iterdir():
            if not j.is_dir():
                continue
            
            for k in j.iterdir():
                if k.name.lower().endswith('pdf'):
                    pdfs.append(k)

    folder = WS / 'pdf'
    folder.mkdir(exist_ok=True)
    for i in pdfs:
        desc = folder / i.name
        copy(str(i), str(desc))
