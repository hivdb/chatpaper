from PyPDF2 import PdfReader
from pathlib import Path
import openai
from dotenv import load_dotenv
import os
import Levenshtein


WS = Path(__file__).resolve().parent.parent

load_dotenv(WS / '.env')


def pdf2text(pdf_file_path):
    reader = PdfReader(pdf_file_path)
    extracted_text = ""
    for page in reader.pages:
        extracted_text += page.extract_text()

    txt_file_path = pdf_file_path.resolve().parent / f"{pdf_file_path.stem}.txt"
    with open(txt_file_path, 'w', encoding='utf-8') as fd:
        fd.write(extracted_text)


def complete_text(question):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": question}
        ],
        temperature=0
    )
    return completion['choices'][0]['message']['content']


def get_question(text, text2):

    return f"""
    Please complete the content enclosed in <> with {len(text2)} characters
    <{text}>
    """


def MELD(text):
    text_length = len(text)

    half_length = int(text_length / 2)
    text1 = text[:half_length]
    text2 = text[half_length:]

    gen_text2 = complete_text(text1)
    distance = calc_match(gen_text2, text2)

    print(f"MELD: {levenshtein_distance(distance, text_length)}")
    print(f"LD: {calculate_string_LD_match(text2, gen_text2)}")


def calc_match(string1, string2):
    match_count = 0
    min_len = min(len(string1), len(string2))

    for i in range(min_len):
        if string1[i] == string2[i]:
            match_count += 1

    return match_count


def calculate_string_LD_match(string1, string2):
    distance = Levenshtein.distance(string1, string2)
    match_percentage = (1 - (distance / max(len(string1), len(string2)))) * 100
    return match_percentage


def levenshtein_distance(num_match, text_length):

    return int(round(2.0 * num_match) * 100 / text_length) / 100


def convert_papers(folder):
    for f in folder.iterdir():
        if f.suffix.lower() != '.pdf':
            continue

        pdf2text(f)


def find_content(keyword, text: str, text_length=1000):
    text = text.lower()

    pos = text.find('introduction')
    if pos < 0:
        return ''
    else:
        pos += len('introduction')
        return text[pos: pos + text_length]


def test_memory(folder):
    for f in folder.iterdir():
        if f.suffix.lower() != '.txt':
            continue

        text = find_content('introduction', open(f).read())
        if not text:
            text = find_content('method', open(f).read())

        if not text:
            continue

        MELD(text)


# def work(folder):
#     test_memory(folder)


# if __name__ == '__main__':
#     folder = Path(__file__).resolve().parent / 'papers'
#     work(folder)
