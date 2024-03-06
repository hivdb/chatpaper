from pathlib import Path
from fpdf import FPDF

directory = Path("./src")

pdf = FPDF()
pdf.set_font("Courier", size=10)


def add_all_files(folder):

    sub_folders = []

    for f in folder.iterdir():
        if f.name == '__init__.py':
            continue

        if f.suffix == ".py":
            add_file_content(pdf, f)
        elif f.is_dir():
            sub_folders.append(f)

    for sf in sub_folders:
        add_all_files(sf)


def add_file_content(pdf, f):

    pdf.add_page()

    pdf.cell(200, 5, txt=f.name, ln=True, align='C')

    with open(f) as file:
        content = file.readlines()

    for line in content:
        if line.strip().startswith('#'):
            continue
        pdf.cell(200, 5, txt=line, ln=True, align='L')


add_all_files(directory)
pdf.output("combined_python_scripts.pdf")
