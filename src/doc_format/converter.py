from PyPDF2 import PdfReader
import subprocess


def pdf2text(source, dest):
    reader = PdfReader(source)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()

    with open(dest, 'w', encoding='utf-8') as fd:
        fd.write(extracted_text)


def docx2md_pandoc(source, dest):
    pass


def docx2html_pandoc(source, dest):
    cmd = [
        'pandoc',
        '-f',
        'docx',
        '-t',
        'html',
        source,
        '-o',
        dest,
    ]
    subprocess.run(cmd)


def html2md_pandoc(source, dest):
    cmd = [
        'pandoc',
        '-f',
        'html',
        '-t',
        'markdown',
        source,
        '-o',
        dest,
    ]
    subprocess.run(cmd)
